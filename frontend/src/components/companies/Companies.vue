<template>
  <div>
    <v-container fluid>
      <v-row>
        <v-col>
          <v-item-group>
            <v-btn small dark fab color="primary" class="ms-2" @click="handleAdd"><v-icon>mdi-plus</v-icon></v-btn>
          </v-item-group>
        </v-col>
        <v-col align="end">
          <v-item-group>
            <v-btn small dark color="warning" class="ms-2" :loading="checkingStoch" @click="handleStoch">Проверить Stoch</v-btn>
          </v-item-group>
        </v-col>
      </v-row>
      <v-data-table
        dense
        :items="list"
        :items-per-page="100"
        :headers="headers"
        item-key="name"
        :disable-pagination="true"
        :hide-default-footer="true"
      >
        <template v-slot:item.num="{ index }">
          {{ index + 1 }}
        </template>
        <template v-slot:item.name="{ item }">
          <div @click="handleEdit(item)">{{ item.name }}</div>
        </template>
        <template v-slot:item.tiker="{ item }">
          <div @click="handleEdit(item)">{{ item.tiker }}</div>
        </template>
        <template v-slot:item.strategies="{ item }">
          <div>{{ item.strategies.map(s => s.name).join(', ') }}</div>
        </template>
        <template v-slot:item.has_mos_index="{ item }">
          <v-icon v-if="item.has_mos_index" color="primary">mdi-check</v-icon>
        </template>
        <template v-slot:item.stops="{ item }">
          <template v-if="item.stops && item.stops.length > 0">
            <v-chip v-for="s in item.stops" :key="s.period" @click="handleEditStops(item)">
              {{ s.period }}: {{ s.value }}
            </v-chip>
          </template>
          <template v-else>
            <v-chip @click="handleEditStops(item)">Нет</v-chip>
          </template>
        </template>
      </v-data-table>
      <company-dialog
        :open="dialog"
        :company-names="companyNames"
        :company-tikers="companyTikers"
        :edit-data="editData"
        :dialog-mode="dialogMode"
        @dialog-cancel="dialog = false"
        @added-company="handleUpdatedDialog"
        @deleted-company="handleUpdatedDialog"
      />
      <company-stops
        :open="dialogStops"
        :name="editData.name"
        :company-id="editData.id"
        :stops="editData.stops"
        @changed-company-stops="handleSaveStopsDialog"
        @closed-stops="dialogStops = false"
      />

    </v-container>

  </div>
</template>

<script>
import {
  getData,
  // getCategoriesSimple,
  endpoints
} from '@/api/invmos-back'
// import { getDividends } from '@/api/open-broker'
import PriceSynchronizer from '@/utils/PriceSynchronizer'
import CompanyDialog from '@/components/companies/CompanyDialog.vue'
import CompanyStops from '@/components/companies/CompanyStops.vue'

export default {
  name: 'Companies',
  components: { CompanyDialog, CompanyStops },
  props: {},
  data() {
    return {
      priceSynchronizer: new PriceSynchronizer(),
      list: [],
      otrasli: [],
      dialog: false,
      dialogStops: false,
      dialogMode: '',
      checkingStoch: false,
      selected: [],
      headers: [
        { text: '№', value: 'num', sortable: false },
        {
          text: 'Название',
          align: 'start',
          value: 'name'
        },
        // {
        //   text: 'Отрасль',
        //   align: 'start',
        //   value: 'otrasl'
        // },
        {
          text: 'Стратегии',
          align: 'start',
          value: 'strategies'
        },
        {
          text: 'Тикер',
          align: 'start',
          value: 'tiker'
        },
        {
          text: 'Стопы',
          align: 'start',
          value: 'stops'
        }
        // ,{
        //   text: 'Индекс МОС биржи',
        //   value: 'has_mos_index',
        //   align: 'center'
        // },
        // { text: 'Валюта', value: 'currency' }
      ],
      editData: {}
    }
  },
  computed: {
    // otrasliKeyMap() {
    //   return this.otrasli.reduce(function(map, obj) {
    //     map[obj.id] = obj
    //     return map
    //   }, {})
    // },
    companyNames() {
      return this.list.map(c => c.name ? c.name.toLowerCase() : '')
    },
    companyTikers() {
      return this.list.map(c => c.tiker.toLowerCase())
    }
  },
  mounted() {
    this.fetchList()
  },
  methods: {
    fetchList() {
      // getCategoriesSimple('otrasli').then(otrasli => {
      //   this.otrasli = otrasli
      // })
      getData(endpoints.COMPANIES, { limit: 500, offset: 0 }).then(data => {
        this.$set(this, 'list', data)
      })
    },
    handleAdd() {
      this.dialogMode = 'add'
      this.editData = {}
      this.dialog = true
    },
    handleEdit(item) {
      this.dialogMode = 'edit'
      this.editData = Object.assign({}, item)
      this.dialog = true
    },
    handleUpdatedDialog() {
      this.dialog = false
      this.fetchList()
    },
    handleEditStops(item) {
      this.editData = Object.assign({}, item)
      this.dialogStops = true
    },
    handleSaveStopsDialog() {
      this.dialogStops = false
      this.$nextTick(() => {
        this.fetchList()
      })
      this.fetchList()
    },
    handleStoch() {
      this.checkingStoch = true
      getData(endpoints.STOCH, { period: 'ALL' }).then((results) => {
        this.checkingStoch = false
        console.log(results)
      })
    }
  }
}
</script>

<style scoped></style>
