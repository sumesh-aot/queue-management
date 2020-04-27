'''Copyright 2018 Province of British Columbia

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.'''

import logging
from flask_restx import Resource
from flask import request, g
from app.schemas.bookings import AppointmentSchema
from app.schemas.theq import CitizenSchema
from app.models.theq import CSR, CitizenState, PublicUser, Citizen, Office
from app.models.bookings import Appointment
from qsystem import api, api_call_with_retry, db, oidc
from app.utilities.snowplow import SnowPlow
from datetime import datetime
from app.utilities.email import send_blackout_email


@api.route("/appointments/", methods=["POST"])
class AppointmentPost(Resource):

    appointment_schema = AppointmentSchema()
    citizen_schema = CitizenSchema()

    @oidc.accept_token(require_token=True)
    @api_call_with_retry
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data received for creating an appointment"}, 400

        is_blackout_appt = json_data.get('blackout_flag', 'N') == 'Y'
        csr = None

        #  Create a citizen for later use.
        citizen = self.citizen_schema.load({}).data
        is_existing_citizen:bool = False

        # Check if the appointment is created by public user. Can't depend on the IDP as BCeID is used by other users as well
        is_public_user_appointment = False
        if json_data.get('user_id', None):
            is_public_user_appointment = True
            office_id = json_data.get('office_id')
            user = PublicUser.find_by_username(g.oidc_token_info['username'])
            # Add values for contact info and notes
            json_data['contact_information'] = user.email
            json_data['comments'] = json_data.get('comments', '') + f'\nPhone: {user.telephone}' if user.telephone else ''

            existing_citizen = Citizen.find_citizen_by_user_id(user.user_id, office_id)
            if existing_citizen:
                citizen = existing_citizen
                is_existing_citizen = True
                office = Office.find_by_id(office_id)
                # Validate if the same user has other appointments for same day at same office
                appointments = Appointment.find_by_citizen_id_and_office_id(office_id=office_id,
                                                                            citizen_id=existing_citizen.citizen_id,
                                                                            start_time=json_data.get('start_time'),
                                                                            timezone=office.timezone.timezone_name)
                if appointments and len(appointments) >= office.max_person_appointment_per_day:
                    return {"code": "MAX_NO_OF_APPOINTMENTS_REACHED", "message": "Maximum number of appoinments reached"}, 400

            else:
                citizen.user_id = user.user_id
                citizen.citizen_name = user.display_name

        else:
            csr = CSR.find_by_username(g.oidc_token_info['username'])
            office_id = csr.office_id

        # Check if there is an appointment for this time
        if json_data.get('blackout_flag', 'N') == 'N':
            conflict_appointments = Appointment.get_appointment_conflicts(office_id, json_data.get('start_time'), json_data.get('end_time'))
            if conflict_appointments:
                return {"code": "CONFLICT", "message": "Conflict while creating appointment"}, 400

        if not is_existing_citizen:
            citizen.office_id = office_id
            citizen.qt_xn_citizen_ind = 0
            citizen_state = CitizenState.query.filter_by(cs_state_name="Appointment booked").first()
            citizen.cs_id = citizen_state.cs_id
            citizen.start_time = datetime.now()
            citizen.service_count = 1

            db.session.add(citizen)
            db.session.commit()

        appointment, warning = self.appointment_schema.load(json_data)
        if is_public_user_appointment:
            appointment.citizen_name = user.display_name

        if warning:
            logging.warning("WARNING: %s", warning)
            return {"message": warning}, 422

        if appointment.office_id == office_id:
            appointment.citizen_id = citizen.citizen_id
            db.session.add(appointment)
            db.session.commit()
            if not is_public_user_appointment:
                SnowPlow.snowplow_appointment(citizen, csr, appointment, 'appointment_create')

            result = self.appointment_schema.dump(appointment)

            # TODO If staff us creating a blackout event then send email to all of the citizens with appointments for that day
            if csr and is_blackout_appt:
                appointments_for_the_day = Appointment.get_appointment_conflicts(office_id, json_data.get('start_time'), json_data.get('end_time'))
                send_blackout_email(appointments_for_the_day)

            return {"appointment": result.data,
                    "errors": result.errors}, 201

        else:
            return {"The Appointment Office ID and CSR Office ID do not match!"}, 403
