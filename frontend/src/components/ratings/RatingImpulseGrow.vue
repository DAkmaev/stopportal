<template>
  <div>
    <v-container fluid>
      <v-row>
        <v-col align="end" />
      </v-row>
      <v-row>
        <v-col>
          <v-data-table
            dense
            :disable-pagination="true"
            :items="list"
            :headers="headers"
            :loading="loading"
          >
            <template v-slot:item.rating="{ item }">
              <v-chip :color="getColor(item.rating, 1)" small>{{ item.rating }}</v-chip>
            </template>
            <template v-slot:item.diff_1m_perc="{ item }">
              {{ item.diff_1m_perc }}%
            </template>
            <template v-slot:item.diff_3m_perc="{ item }">
              {{ item.diff_3m_perc }}%
            </template>
            <template v-slot:item.diff_6m_perc="{ item }">
              {{ item.diff_6m_perc }}%
            </template>
            <template v-slot:item.diff_1y_perc="{ item }">
              {{ item.diff_1y_perc }}%
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { getData, endpoints } from '@/api/invmos-back'
import { getRatingColor } from '@/utils/ratingFiller'
export default {
  name: 'RatingImpulseGrow',
  data() {
    return {
      list: [],
      loading: false,
      headers: [
        { text: 'Комапания', value: 'name' },
        { text: 'Отрасль', value: 'otrasl_name' },
        { text: 'min за 52 недели', value: 'min_price', align: 'center', width: 30 },
        { text: 'max за 52 недели', value: 'max_price', align: 'center', width: 30 },
        { text: 'текущая цена', value: 'cur_price', align: 'center', width: 30 },
        { text: 'изменение за год', value: 'diff_1y_perc', align: 'center', width: 30 },
        { text: 'изменение за 1 месяц', value: 'diff_1m_perc', align: 'center', width: 30 },
        { text: 'изменение за 3 месяца', value: 'diff_3m_perc', align: 'center', width: 30 },
        { text: 'изменение за 6 месяцев', value: 'diff_6m_perc', align: 'center', width: 30 },
        { text: 'Рейтинг импульса', value: 'rating', align: 'center', width: 30 },
        { text: 'Индекс мосбиржи', value: 'has_mos_index', align: 'center', width: 30 }
      ]
    }
  },
  created() {
    this.fetchList()
  },
  methods: {
    async fetchList() {
      this.loading = true
      this.list = await getData(endpoints.RATINGS_IMPULSE_GROW)
      this.loading = false
    },
    getColor(figure, multiple = 1) {
      return getRatingColor(figure, multiple)
    }
  }
}
</script>

<style scoped>

</style>
