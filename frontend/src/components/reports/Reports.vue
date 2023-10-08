<template>
  <v-container fluid>
    <v-row>
      <v-col cols="3">
        <v-autocomplete
          v-model="companyId"
          no-data-text="Нет данных"
          label="Выберите компанию"
          :items="companies"
          item-text="name"
          item-value="id"
          clearable
        />
      </v-col>
    </v-row>
    <v-tabs v-model="tab" centered grow>
      <v-tab v-for="(n,i) in reports" :key="i">
        {{ n.text }}
      </v-tab>
      <v-tab>
        Коэффициенты
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item v-for="report in reports" :key="report.name">
        <report
          :report-type="report.name"
          :company-id="companyId"
        />
      </v-tab-item>
      <v-tab-item>
        <report-coefficient
          :company-id="companyId"
        />
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script>
import { getData, endpoints } from '@/api/invmos-back'
import Report from './Report'
import ReportCoefficient from '@/components/reports/ReportCoefficient'
export default {
  name: 'Reports',
  components: { ReportCoefficient, Report },
  data() {
    return {
      tab: 0,
      companies: [],
      companyId: 1,
      reports: [
        { name: 'balance', text: 'Баланс' },
        { name: 'piu', text: 'Прибыль и убытки' },
        { name: 'dds', text: 'ДДС' }
      ]
    }
  },
  created() {
    this.fetchCompanies()
  },
  methods: {
    fetchCompanies() {
      getData(endpoints.COMPANIES, { fields: 'c.id,c.name,c.tiker' }).then(data => {
        this.companies = data
      })
    }
  }
}
</script>

<style scoped>

</style>
