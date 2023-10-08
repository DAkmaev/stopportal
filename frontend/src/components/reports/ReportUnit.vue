<template>
  <div>
    <v-select
      v-model="unit"
      :items="units"
      item-text="id"
      item-value="id"
      label="Единицы измерения"
      return-object
      @change="setUnit"
    />
  </div>
</template>

<script>
import { getData, putData, endpoints } from '@/api/invmos-back'

export default {
  name: 'ReportUnit',
  props: {
    reportType: {
      type: String,
      default: undefined
    },
    companyId: {
      type: Number,
      default: undefined
    }
  },
  data() {
    return {
      units: [
        { id: 'руб.', multiplier: 1 },
        { id: 'тыс.руб.', multiplier: 1000 },
        { id: 'млн.руб.', multiplier: 1000000 },
        { id: 'млрд.руб.', multiplier: 1000000000 }
      ],
      unit: undefined
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      getData(endpoints.REPORTS_UNITS, { type: this.reportType, companyId: this.companyId })
        .then(data => {
          this.unit = data && data.length > 0 ? this.units.find(u => u.id === data[0].unit) : null
          this.$emit('report-unit-updated', this.unit ? this.unit.multiplier : 1)
        })
    },
    setUnit() {
      putData(endpoints.REPORTS_UNITS, {}, false, { type: this.reportType, companyId: this.companyId, unitId: this.unit.id })
        .then(
          this.$emit('report-unit-updated', this.unit ? this.unit.multiplier : 1)
        )
    }
  }/*,
  computed: {
    unit: function () {
      this.unitIndex ? this.units.find(u => u.id === this.unitIndex) : null
    }
  }*/

}
</script>

<style scoped>

</style>
