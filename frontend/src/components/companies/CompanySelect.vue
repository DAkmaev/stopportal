<template>
  <div>
    <v-autocomplete
      :value="company"
      no-data-text="Нет данных"
      :label="label"
      :items="filteredList"
      item-text="name"
      item-value="id"
      return-object
      clearable
      @change="handleChangeCompany"
    />
  </div>
</template>

<script>
import { getData, endpoints } from '@/api/invmos-back'
import { mapGetters } from 'vuex'

export default {
  name: 'CompanySelect',
  props: {
    company: {
      type: Number,
      default: undefined
    },
    label: {
      type: String,
      default: 'Выберите компанию'
    },
    strategyIds: {
      type: Array,
      default: () => []
    },
    notStrategyIds: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      companies: []
    }
  },
  computed: {
    ...mapGetters(['token']),
    filteredList: function() {
      if (this.companies.length > 0 && (this.strategyIds.length > 0 || this.notStrategyIds.length > 0)) {
        return this.companies.filter(c => {
          const hasRequiredStrategies = this.strategyIds.length > 0 ? this.strategyIds.some(s => c.strategies_ids.includes(s)) : true
          const noBlackListStrategies = this.notStrategyIds.every(s => !c.strategies_ids.includes(s))
          return hasRequiredStrategies && noBlackListStrategies
        })
      }
      return this.companies
    }
  },
  created() {
    this.fetchList()
  },
  methods: {
    fetchList() {
      getData(endpoints.COMPANIES, { fields: 'c.id,c.name,c.tiker,c.currency,c.issue_size,c.capitalization' }, this.token).then(data => {
        this.companies = data
      })
    },
    handleChangeCompany(val) {
      this.$emit('company-changed', val)
    }
  }
}
</script>

<style scoped>

</style>
