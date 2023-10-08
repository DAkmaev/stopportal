<template>
  <v-container fluid>
    <h3>Статьи в отчетах</h3>
    <v-tabs v-model="tab" centered grow>
      <v-tab v-for="(n,i) in reports" :key="i">
        {{ n.text }}
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item v-for="report in reports" :key="report.name">
        <company-categories
          :company-id="companyId"
          :report-type="report.name"
        />
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script>
import CompanyCategories from './CompanyCategories'
export default {
  name: 'CompanyCategoriesList',
  components: { CompanyCategories },
  props: {
    companyId: {
      type: Number,
      default: undefined
    }
  },
  data() {
    return {
      tab: undefined,
      reports: [
        { name: 'balance', text: 'Баланс' },
        { name: 'piu', text: 'ПиУ' },
        { name: 'ddu', text: 'ДДУ' }
      ]
    }
  }
}
</script>

<style scoped>

</style>
