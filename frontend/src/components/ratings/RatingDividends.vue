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
            <!-- <template v-slot:item.indexGrow="{ item }">
              <v-chip :color="getColor(item.indexGrow, 2)" small>{{ item.indexGrow }}</v-chip>
            </template>
            <template v-slot:item.indexStab="{ item }">
              <v-chip :color="getColor(item.indexStab, 2)" small>{{ item.indexStab }}</v-chip>
            </template>-->
            <template v-slot:item.rating="{ item }">
              <v-chip :color="getColor(item.rating, 1)" small>{{ item.rating }}</v-chip>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { getData, endpoints } from '@/api/invmos-back'

export default {
  name: 'RatingDividends',
  data() {
    return {
      dates: [],
      years: [],
      list: [],
      headers: [],
      loading: false
    }
  },
  created() {
    this.fetchList()
  },
  methods: {
    async fetchList() {
      this.loading = true
      const [columns, data] = await getData(endpoints.DIVIDENDS_OVERALL)
      await this.fillHeaders(columns)
      this.list = data
      this.loading = false
    },
    async fillHeaders(years) {
      this.years = years
      this.headers = [
        { text: 'Комапания', value: 'name' },
        ...this.years.map(y => ({ text: `${y}`, value: `${y}` })),
        { text: 'Стабильность роста', value: 'indexGrow', align: 'center', width: 30 },
        { text: 'Стабильность выплат', value: 'indexStab', align: 'center', width: 30 },
        { text: 'Рейтинг стабильности дивидендов', value: 'rating', align: 'center', width: 30 }
      ]
    },
    getColor(figure, multiple) {
      switch (figure * multiple) {
        case 0:
        case 1:
        case 2:
          return 'red lighten-3'
        case 3:
        case 4:
          return 'deep-orange lighten-3'
        case 5:
        case 6:
          return 'amber lighten-3'
        case 7:
        case 8:
          return 'lime lighten-3'
        case 9:
        case 10:
          return 'green lighten-3'
      }
    }
  }
}
</script>

<style scoped>

</style>
