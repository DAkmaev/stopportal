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
                  clearable
                  :label="periodNames[period]"
                  v-model="temp[period].value"
              >{{temp[period].value}}</v-text-field>
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
export default {
  name: 'CompanyStops',
  props: {
    open: Boolean,
    name: {
      type: String,
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
  computed: {},
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
      const diffValues = Object.keys(this.temp).filter(period => {
        const existStop = this.stops.find(s => s.period === period)
        const newStopValue = this.temp[period].value
        return !!newStopValue && !existStop || existStop && existStop.value !== newStopValue
      })
      // const diffValues = this.stops.filter(s => {
      //   const editValue = this.temp[s.period].value
      //   return editValue !== null && s.value !== null && editValue !== s.value
      // })
      console.log(diffValues)
    }
  }
}
</script>

<style scoped>

</style>
