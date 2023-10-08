<template>
  <div>
    <v-container fluid>
      <v-row>
        <v-col align="start" cols="2">
          <report-unit :company-id="companyId" :report-type="reportType" @report-unit-updated="unitSaved" />
        </v-col>
        <v-col align="end">
          <v-btn
            v-if="!editMode && companyId"
            color="warning"
            @click="editMode = true"
          >Категории</v-btn>
          <v-btn
            v-if="editMode"
            color="info"
            @click="editMode = false"
          >Закрыть</v-btn>
          <v-btn
            v-if="!editMode && companyId"
            style="margin-left: 10px"
            color="primary"
            :disabled="list.length === 0"
            @click="dialog = true"
          >Добавить период</v-btn>

        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-data-table
            v-if="!editMode"
            dense
            :disable-pagination="true"
            :items="list"
            :headers="headers"
          >
            <template v-slot:item="{item}">
              <tr :class="getRowClass(item)">
                <td v-for="(col, columnIndex) in headers" :key="columnIndex">
                  <div v-if="columnIndex === 0">{{ item.id }}</div>
                  <div v-else-if="columnIndex === 1">{{ item[col.value] }}</div>
                  <div v-else-if="!item.company_category_id" />
                  <v-edit-dialog
                    v-else
                    :return-value.sync="item[col.value]"
                    @save="saveValue(item.company_category_id, col.id, item[col.value])"
                    @cancel="cancelChange"
                  > {{ item[col.value] }}
                    <template v-slot:input>
                      <v-text-field
                        v-model="item[col.value]"
                        label="Изменить"
                        single-line
                        counter
                      />
                    </template>
                  </v-edit-dialog>
                </td>
              </tr>
            </template>

          </v-data-table>
          <company-categories
            v-else
            :company-id="companyId"
            :report-type="reportType"
            @save-categories="handleSaveCategories"
            @cancel-save="editMode = false"
          />
        </v-col>
      </v-row>
    </v-container>
    <v-dialog
      v-model="dialog"
      max-width="480"
    >
      <v-card>
        <v-card-title class="headline">Выберите дату</v-card-title>
        <v-card-text align="center">
          <v-date-picker v-model="dialogDate" full-width />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            color="darken-1"
            text
            @click="dialog = false"
          >Отменить</v-btn>
          <v-btn
            color="green darken-1"
            text
            @click="addDate"
          >Добавить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-snackbar
      v-model="snackbar.enable"
      :color="snackbar.color"
      top
      right
      :timeout="6000"
    >
      {{ snackbar.text }}
      <v-btn
        dark
        text
        @click="snackbar.enable = false"
      >
        X
      </v-btn>
    </v-snackbar>
  </div>
</template>

<script>
import { getData, putData, postData, endpoints } from '@/api/invmos-back'
import { nest, flattenTree } from '@/utils/tree'
import CompanyCategories from '@/components/companies/CompanyCategories'
import ReportUnit from './ReportUnit'

export default {
  name: 'Report',
  components: { CompanyCategories, ReportUnit },
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
      dates: [],
      list: [],
      baseList: [],
      tree: [],
      dialog: false,
      dialogDate: undefined,
      editMode: false,
      multiplier: 1,
      snackbar: {
        enable: false,
        text: '',
        color: 'success'
      }
    }
  },
  computed: {
    headers: function() {
      const columns = [
        {
          text: 'id',
          align: 'start',
          sortable: false,
          width: 30,
          value: 'id'
        },
        {
          text: 'Название',
          align: 'start',
          sortable: false,
          value: 'name'
        }
      ]
      this.dates.forEach(d => {
        columns.push({
          text: new Date(d.date).toLocaleString('sv').substr(0, 10),
          align: 'start',
          sortable: false,
          value: `d_${d.id}`,
          id: d.id
        })
      })
      return columns
    }
  },
  watch: {
    companyId: function() {
      if (this.companyId !== undefined) { this.fetchList() }
    },
    multiplier: function() {
      this.multiplyList()
    }
  },
  created() {
    if (this.companyId) { this.fetchList() }
  },
  mounted() {},
  methods: {
    async fetchList() {
      this.dates = await getData(endpoints.REPORTS_COLUMNS, { type: this.reportType, companyId: this.companyId })
      getData(endpoints.REPORTS_VALUES, {
        reportType: this.reportType,
        companyId: this.companyId,
        dates: this.dates.join(',')
      })
        .then(data => {
          this.tree = nest(data)
          this.baseList = flattenTree(this.tree)
          this.multiplyList()
        })
    },
    saveValue(catId, colId, newValue) {
      putData(endpoints.REPORTS_VALUES, {}, false, { categoryId: catId, companyId: colId, value: newValue * this.multiplier })
        .then(() => {
          this.snackbar.text = 'Успешно сохранено'
          this.snackbar.color = 'success'
          this.snackbar.enable = true
          this.fetchList()
        })
    },
    cancelChange() {
      console.log('cancel')
    },
    async addDate() {
      postData(endpoints.REPORTS_COLUMNS, {}, false, { type: this.reportType, companyId: this.companyId, date: this.dialogDate }).then(() => {
        this.fetchList()
        this.dialog = false
        this.snackbar.text = 'Успешно добавлено'
        this.snackbar.color = 'success'
        this.snackbar.enable = true
      })
    },
    getRowClass(item) {
      return !item.company_category_id ? 'company-row-group' : ''
    },
    handleSaveCategories() {
      this.editMode = false
      this.fetchList()
    },
    unitSaved(multiplier) {
      if (multiplier) { this.multiplier = multiplier }
    },
    multiplyList() {
      this.list = this.baseList.map((l) => {
        const newL = Object.assign({}, l)
        Object.keys(newL).forEach(p => {
          if (newL[p] && p.startsWith('d_')) {
            newL[p] = newL[p] / this.multiplier
          }
        })
        return newL
      })
    }
  }
}
</script>

<style scoped>
  .company-row-group {
    font-weight: bold;
    background-color: #e6e6ea;
  }

</style>
