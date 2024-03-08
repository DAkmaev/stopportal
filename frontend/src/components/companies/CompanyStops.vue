<template>
  <v-dialog v-if="open" v-model="temp" width="auto">
    <v-card>
      <v-card-title>
        Изменить стопы для {{ name }}
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-row v-for="period in Object.keys(temp)" :key="period">
            <v-col cols="8">
              <v-text-field
                v-model="temp[period].value"
                clearable
                :label="periodNames[period]"
              >{{ temp[period].value }}</v-text-field>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="handleCancel">Отмена</v-btn>
        <v-btn text color="primary" @click="saveStops">Сохранить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { endpoints, postData, deleteData, putData } from '@/api/invmos-back'
import { mapGetters } from 'vuex'

export default {
  name: 'CompanyStops',
  props: {
    open: Boolean,
    name: {
      type: String,
      default: undefined
    },
    companyId: {
      type: Number,
      default: undefined
    },
    stops: {
      type: Array,
      default: () => ([])
    }
  },
  data() {
    return {
      temp: {},
      periodNames: {
        'D': 'День',
        'W': 'Неделя',
        'M': 'Месяц'
      }
    }
  },
  computed: {
    ...mapGetters(['token'])
  },
  watch: {
    open: function() {
      this.resetTemp()
      if (this.stops) {
        for (const stop of this.stops) {
          const { period, id, value } = stop
          this.temp[period] = { id, value }
        }
      }
    },
    temp: function() {
      if (!this.temp) {
        this.$emit('closed-stops')
      }
    }
  },
  methods: {
    resetTemp() {
      this.temp = {
        'D': { 'id': null, 'value': null },
        'W': { 'id': null, 'value': null },
        'M': { 'id': null, 'value': null }
      }
    },
    handleCancel() {
      this.$emit('closed-stops')
    },
    saveStops() {
      const stops_remove_ids = this.stops
        .filter(stop => this.temp[stop.period] && this.temp[stop.period].value === null)
        .map(stop => stop.id)

      const stops_new = Object.keys(this.temp)
        .filter(period => !this.stops.some(stop => stop.period === period) && this.temp[period].value !== null)
        .map(period => ({
          'company_id': this.companyId,
          'period': period,
          'value': this.temp[period].value
        }))

      const stops_updated = Object.keys(this.temp)
        .filter(period => this.stops.some(stop => stop.period === period && this.temp[period].value !== null))
        .map(period => ({
          'id': this.temp[period].id,
          'company_id': this.companyId,
          'period': period,
          'value': this.temp[period].value
        }))

      const tasks = []
      stops_remove_ids.forEach(id => {
        tasks.push(deleteData(endpoints.STOPS + id, null, this.token))
      })

      stops_new.forEach(s => {
        tasks.push(postData(endpoints.STOPS, s, null, this.token))
      })

      stops_updated.forEach(s => {
        tasks.push(putData(endpoints.STOPS, s, null, this.token))
      })

      Promise.all(tasks)
        .then(this.$emit('changed-company-stops'))
        .catch(err => {
          console.error(err)
        })
      // patchData(endpoints.COMPANIES + this.companyId, { 'stops': stops }, false)
      //     .then(() => {
      //       this.$emit('changed-company-stops')
      //     })
      //     .catch(err => {
      //       console.error(err)
      //     })

      // const stops_updated = Object.keys(this.temp)
      //     .filter(period => this.stops.some(stop => stop.period === period && this.temp[period].value !== null))
      //     .map(period => ({
      //       "id": this.temp[period].id,
      //       "company_id": this.companyId,
      //       "period": period,
      //       "value": this.temp[period].value
      //     }));
    }
  }
}
</script>

<style scoped>

</style>
