<template>
  <div :class="{'service-selection-mobile': $vuetify.breakpoint.xs}">
    <v-card-text>
      <v-row justify="center">
        <v-col cols="12" sm="6" class="text-center">
          <v-combobox
            :items="serviceList"
            :item-text="'external_service_name'"
            :filter="serviceSearchFilter"
            label="Select Service"
            outlined
            color="primary"
            class="service-selection"
            v-model="selectedService"
            name="service-select"
            @change="serviceSelection"
            @input="clickSelection"
            hide-details
          >
            <template v-slot:selection="data">
              {{ data.item.external_service_name }}
              <span v-if="checkDisabled(data.item)" class="ml-1 caption">(Unavailable)</span>
            </template>
            <template v-slot:item="data">
              <div
                v-bind:class="{'disabled-selection': checkDisabled(data.item)}"
                class="service-selection-options"
              >
                <div>{{ data.item.external_service_name }}</div>
                <div v-if="data.item.online_link" class="service-link" :class="{'service-link-mobile': $vuetify.breakpoint.xs}" @click="goToServiceLink(data.item.online_link)">
                  Online Option <v-icon small>mdi-open-in-new</v-icon>
                </div>
              </div>
            </template>
          </v-combobox>
          <!-- <v-btn
            v-if="selectedService && selectedService.online_link"
            text
            link
            color="primary"
            target="_blank"
            :href="selectedService.online_link"
          >
            Click here for more options
            <v-icon small class="ml-1">mdi-open-in-new</v-icon>
          </v-btn> -->
        </v-col>
      </v-row>
      <v-row justify="center">
        <v-col cols="12" sm="6">
          <v-textarea
            class="mt-3"
            outlined
            name="additional-options"
            label="Is there any additional info you'd like to add? (Optional)"
            v-model="additionalOptions"
            @change="changeAdditionalOptions"
        ></v-textarea>
        </v-col>
      </v-row>
      <template v-if="selectedService">
        <p class="text-center mb-6">Do you want to book an appointment with <strong>{{currentOffice.office_name}}</strong> for <strong>{{selectedService.external_service_name}}</strong> service?</p>
        <div class="d-flex justify-center mb-6">
          <!-- <v-btn
            large
            outlined
            color="primary"
            class="mr-3"
            @click="otherBookingOptionModel = true"
          >No, Book With Another Option</v-btn> -->
          <v-btn
            large
            @click="proceedBooking"
            color="primary"
          >
            Yes, Book With The Service BC Centre
            <v-icon right small class="ml-1">mdi-arrow-right</v-icon>
          </v-btn>
        </div>
        <p class="text-center body-2">
          Information is collected under the authority of
          <a href="http://www.bclaws.ca/civix/document/id/complete/statreg/96165_03#d2e3154" target="_blank">Sections 26(c)</a>
          of the Freedom of Information and Protection of Privacy Act to help us assess and respond to your enquiry. Questions about the collection of information can be directed to the Director, Provincial Operations, PO BOX 9412 STN PROV GOVT, Victoria, BC, V8W 9V1, 1 800 663-7867.
        </p>
      </template>
    </v-card-text>
    <!-- Other Booking Option Model Popup -->
    <v-dialog
      v-model="otherBookingOptionModel"
      max-width="600"
    >
      <v-card>
        <v-toolbar flat color="grey lighten-3">
          <v-toolbar-title>Other Booking Options for BC Services Card</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn icon @click="otherBookingOptionModel = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-toolbar>
        <v-card-text>
          <p class="mt-4 mb-6">Please use one of the below methods to book your appointment</p>
          <p>
            <strong>Phone: </strong> (250)-387-6121
          </p>
          <p>
            <strong>Email: </strong> info@gov.bc.ca
          </p>
          <p>
            <strong>Fax: </strong> (250)-952-4124
          </p>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { Component, Mixins, Prop, Vue } from 'vue-property-decorator'
import { mapActions, mapMutations, mapState } from 'vuex'
import { Office } from '@/models/office'
import { Service } from '@/models/service'
import { ServiceAvailability } from '@/utils/constants'
import StepperMixin from '@/mixins/StepperMixin.vue'

@Component({
  computed: {
    ...mapState('office', [
      'currentOffice',
      'currentService',
      'additionalNotes',
      'serviceList'
    ])
  },
  methods: {
    ...mapMutations('office', [
      'setCurrentService',
      'setAdditionalNotes'
    ]),
    ...mapActions('office', [
      'getServiceByOffice'
    ])
  }
})
export default class ServiceSelection extends Mixins(StepperMixin) {
  private readonly serviceList!: Service[]
  private readonly currentOffice!: Office
  private readonly currentService!: Service
  private readonly additionalNotes!: string
  private readonly setCurrentService!: (service: Service) => void
  private readonly setAdditionalNotes!: (notes: string) => void
  private readonly getServiceByOffice!: (officeId: number) => Promise<Service[]>
  private selectedService: Service = null
  private additionalOptions = ''
  private otherBookingOptionModel = false

  private async mounted () {
    if (this.isOnCurrentStep) {
      if (this.currentOffice?.office_id) {
        await this.getServiceByOffice(this.currentOffice.office_id)
      }
      this.selectedService = (!this.checkDisabled(this.currentService)) ? this.currentService : null
      this.additionalOptions = this.additionalNotes || ''
    }
  }

  private serviceSelection (value) {
    this.setCurrentService(value)
  }

  private clickSelection (value) {
    if (this.checkDisabled(value)) {
      this.selectedService = null
      this.setCurrentService(undefined)
    } else {
      this.setCurrentService(value)
    }
  }

  private changeAdditionalOptions () {
    this.setAdditionalNotes(this.additionalOptions)
  }

  private proceedBooking () {
    this.stepNext()
  }

  private checkDisabled (value) {
    return (value?.online_availability === ServiceAvailability.DISABLE)
  }

  private goToServiceLink (url) {
    window.open(url, '_blank')
  }

  private serviceSearchFilter (item, queryText, itemText) {
    return `${item?.external_service_name || ''} ${item?.service_desc || ''}`.toLowerCase().indexOf((queryText || '').toLowerCase()) > -1
  }
}
</script>

<style lang="scss" scoped>
@import "@/assets/scss/theme.scss";
.v-list-item {
  border-bottom: 1px solid $gray6;
}
.service-message {
  font-size: 10px;
  font-style: italic;
  margin-bottom: 8px;
  max-width: 450px;
}
.disabled-selection {
  color: rgba(0, 0, 0, 0.38);
}
.service-selection-options {
  width: 100%;
  border-bottom: 1px solid $gray2;
  padding-bottom: 6px;
  padding-top: 4px;
  .service-link {
    font-weight: 600;
    font-size: .85rem;
    display: block;
    float: right;
    padding: 8px;
    padding-right: 4px;
    padding-left: 14px;
    margin-top: -10px;
    color: $BCgovBlue8;
    word-break: normal;
  }
}

.service-link-mobile {
  margin-top: 0 !important;
  margin-bottom: -4px;
}
</style>
