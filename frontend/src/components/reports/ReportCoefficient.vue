<template>
  <v-container fluid>
    <v-row>
      <v-col align="start">
        <v-item-group v-if="companyId">
          <v-btn
            color="primary"
            class="ms-2"
            @click="handleAdd(null, null)"
          >Добавить</v-btn>
          <v-btn
            style="margin-left: 10px"
            color="teal"
            dark
            :disabled="list.length === 0 || dates.length === 0"
            @click="handleCopy"
          >Копировать</v-btn>
        </v-item-group>
      </v-col>
      <v-col align="end" cols="2">
        <report-unit :company-id="companyId" report-type="coefficient" @report-unit-updated="unitSaved" />
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-data-table
          dense
          :items="list"
          :items-per-page="50"
          :headers="headers"
          item-key="id"
        >
          <!--          <template v-slot:item.value="{ item }">
            <span>{{ countValue(item.value) }}</span>
          </template>-->
          <template v-slot:item="{item}">
            <tr>
              <td v-for="(col, columnIndex) in headers" :key="columnIndex">
                <div v-if="columnIndex === 0">{{ item.coefficient.id }}</div>
                <div v-else-if="columnIndex === 1">{{ item.coefficient.name }}</div>
                <div v-else style="cursor: pointer">
                  <div v-if="item.values[col.value]" @click="handleEdit(item, col.value)">
                    {{ countValue(item.values[col.value]) }}
                  </div>
                  <div v-else style="color: lightgray" @click="handleAdd(item.coefficient.id, localDateFromString(col.value))">
                    ---------
                  </div>
                </div>
              </td>
            </tr>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
    <v-dialog v-if="dialogEdit" v-model="dialogEdit" :eager="true" scrollable max-width="980px">
      <v-card>
        <v-card-title>
          {{ dialogEditModes[dialogEditMode] }}
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-form ref="addForm" v-model="valid" lazy-validation>
              <v-row class="d-flex justify-center align-center">
                <v-col cols="12" sm="8" md="8">
                  <v-autocomplete
                    v-model="temp.coefficient_id"
                    no-data-text="Нет данных"
                    label="Выберите категорию"
                    :items="coefficients"
                    item-text="name"
                    item-value="id"
                    clearable
                  />
                </v-col>
                <v-col cols="12" sm="8" md="4">
                  <v-menu
                    ref="menu"
                    v-model="datePickerDialog"
                    :close-on-content-click="false"
                    :return-value.sync="temp.date"
                    transition="scale-transition"
                  >
                    <template v-slot:activator="{ on, attrs }">
                      <v-text-field
                        v-model="temp.date"
                        label="Выберите дату"
                        prepend-icon="mdi-calendar"
                        readonly
                        v-bind="attrs"
                        v-on="on"
                      />
                    </template>
                    <v-date-picker
                      v-model="temp.date"
                      no-title
                      scrollable
                      @input="$refs.menu.save(temp.date)"
                    />
                  </v-menu>
                </v-col>
              </v-row>
              <v-row class="d-flex justify-center align-center">
                <v-col cols="12" sm="12" md="6">
                  <v-select
                    v-model="temp.coefficient_formula_id"
                    :disabled="!temp.coefficient_id || !!temp.value"
                    :items="coefficientFormulas"
                    item-text="value"
                    item-value="id"
                    label="Выберите формулу"
                  />
                </v-col>
                <v-col cols="12" sm="12" md="6">
                  <v-text-field
                    v-model="temp.value"
                    label="Ручное значение"
                    clearable
                  />
                </v-col>
              </v-row>
              <v-card-actions>
                <v-spacer />
                <v-btn text color="warning" @click="handleDelete">Удалить</v-btn>
                <v-btn text @click="handleCancel">Отмена</v-btn>
                <v-btn text :disabled="!valid" color="primary" @click="saveItem">Сохранить</v-btn>
              </v-card-actions>
            </v-form>
          </v-container>
        </v-card-text>
      </v-card>
    </v-dialog>
    <v-dialog v-if="dialogCopy" v-model="dialogCopy" :eager="true" scrollable max-width="980px">
      <v-card>
        <v-card-title>Копировать данные</v-card-title>
        <v-card-text>
          <v-container>
            <v-form ref="copyForm" v-model="validCopy">
              <v-row class="d-flex justify-center align-center">
                <v-col cols="12" sm="8" md="4">
                  <v-select
                    v-model="tempCopy.sourceDate"
                    :items="datesLocalStrings"
                    :rules="rulesCopy.sourceDate"
                    label="Выберите дату"
                  />
                </v-col>
                <v-col cols="12" sm="8" md="4">
                  <v-menu
                    ref="menu"
                    v-model="datePickerDialog"
                    :close-on-content-click="false"
                    :return-value.sync="tempCopy.targetDate"
                    transition="scale-transition"
                  >
                    <template v-slot:activator="{ on, attrs }">
                      <v-text-field
                        v-model="tempCopy.targetDate"
                        :rules="rulesCopy.targetDate"
                        required
                        label="Выберите новую дату"
                        prepend-icon="mdi-calendar"
                        readonly
                        v-bind="attrs"
                        v-on="on"
                      />
                    </template>
                    <v-date-picker
                      v-model="tempCopy.targetDate"
                      :rules="rulesCopy.targetDate"
                      no-title
                      scrollable
                      @input="$refs.menu.save(tempCopy.targetDate)"
                    />
                  </v-menu>
                </v-col>
              </v-row>
              <v-card-actions>
                <v-spacer />
                <v-btn text @click="handleCopyCancel">Отмена</v-btn>
                <v-btn text :disabled="!validCopy" color="primary" @click="copyItems">Сохранить</v-btn>
              </v-card-actions>
            </v-form>
          </v-container>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { getData, postData, putData, deleteData, endpoints } from '@/api/invmos-back'
import { fillReportCoefficientFormulas } from '@/utils/coefficientFiller'
import ReportUnit from './ReportUnit'
export default {
  name: 'ReportCoefficient',
  components: { ReportUnit },
  props: {
    companyId: {
      type: Number,
      default: undefined
    }
  },
  data() {
    return {
      dates: [],
      list: [],
      coefficients: [],
      multiplier: 1,
      dialogEditMode: undefined,
      dialogEdit: false,
      dialogCopy: false,
      valid: true,
      validCopy: true,
      datePickerDialog: false,
      dialogEditModes: {
        add: 'Добавить',
        edit: 'Редактировать'
      },
      temp: {
        id: undefined,
        date: undefined,
        coefficient_id: undefined,
        coefficient_formula_id: undefined,
        value: undefined
      },
      tempCopy: {
        sourceDate: undefined,
        targetDate: undefined
      },
      rules: { nameRules: [v => !!v || 'Имя обязательно'] },
      rulesCopy: {
        sourceDate: [v => !!v || 'Дата обязательна'],
        targetDate: [v => !!v || 'Дата обязательна']
      }
    }
  },
  computed: {
    coefficientFormulas() {
      return this.temp.coefficient_id ? this.coefficients.find(c => c.id === this.temp.coefficient_id).formulas : []
    },
    headers() {
      const columns = [
        {
          text: 'id',
          align: 'start',
          sortable: false,
          width: 30,
          value: 'coefficient.id'
        },
        {
          text: 'Название',
          align: 'start',
          sortable: false,
          value: 'coefficient.name'
        }
      ]
      if (this.dates) {
        this.dates.forEach(d => {
          columns.push({
            text: this.localDateFromString(d.date),
            align: 'start',
            sortable: false,
            value: d.date,
            id: d.date
          })
        })
      }
      return columns
    },
    datesLocalStrings() {
      return this.dates ? this.dates.map(d => this.localDateFromDate(d.date.toLocaleString('sv').substr(0, 10))) : []
    }
  },
  watch: {
    companyId: function() {
      if (this.companyId) { this.fetchList() } else {
        this.dates = []
        this.list = []
      }
    },
    multiplier: function() {
      this.fetchList()
    }
  },
  created() {
    this.fetchList()
  },
  methods: {
    async fetchList() {
      if (this.companyId) {
        this.dates = await getData(endpoints.COEFFICIENTS_VALUES_DATES, { companyId: this.companyId })
        const data = await getData(endpoints.COEFFICIENTS_VALUES, { companyId: this.companyId })
        this.list = await fillReportCoefficientFormulas(data, this.companyId, this.multiplier)
        this.coefficients = await getData(endpoints.COEFFICIENTS)
      }
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        date: undefined,
        coefficient_id: undefined,
        coefficient_formula_id: undefined,
        value: undefined
      }
    },
    handleAdd(coefficientId, date) {
      this.resetTemp()
      if (coefficientId) { this.temp.coefficient_id = coefficientId }
      if (date) { this.temp.date = date }
      this.dialogEditMode = 'add'
      this.dialogEdit = true
    },
    saveItem() {
      if (this.dialogEditMode === 'add') this.addItem()
      else this.editItem()
    },
    addItem() {
      postData(endpoints.COEFFICIENTS_VALUES, this.getMultipliedTemp(), false, { companyId: this.companyId })
        .then(() => {
          this.fetchList()
          this.dialogEdit = false
        })
        .catch(err => {
          console.error(err)
        })
    },
    handleCancel() {
      this.dialogEdit = false
    },
    handleEdit(item, date) {
      this.dialogEditMode = 'edit'
      const multiplyValue = value => Number.parseFloat(value) ? (Number.parseFloat(value) / this.multiplier).toString() : value
      this.temp = {
        id: item.values[date].id,
        date: date.toLocaleString('sv').substr(0, 10),
        coefficient_id: item.coefficient.id,
        coefficient_formula_id: item.values[date].formula ? item.values[date].formula.id : null,
        value: item.values[date].value ? multiplyValue(item.values[date].value) : null
      }
      this.dialogEdit = true
    },
    editItem() {
      putData(endpoints.COEFFICIENTS_VALUES, this.getMultipliedTemp(), false)
        .then(() => {
          this.fetchList()
          this.dialogEdit = false
        })
        .catch(err => {
          console.error(err)
        })
    },
    handleDelete() {
      confirm('Вы точно хотите удалить?') &&
      deleteData(endpoints.COEFFICIENTS_VALUES, { id: this.temp.id }).then(() => {
        this.active = []
        this.fetchList()
        this.dialogEdit = false
        console.log(`Deleted`)
      })
    },
    handleCopy() {
      this.tempCopy.sourceDate = this.localDateFromDate(this.dates[this.dates.length - 1].date)
      this.tempCopy.targetDate = undefined
      this.dialogCopy = true
      this.validCopy = false
    },
    copyItems() {
      postData(endpoints.COEFFICIENTS_VALUES_COPY, {}, false, {
        sourceDate: this.tempCopy.sourceDate,
        targetDate: this.tempCopy.targetDate,
        companyId: this.companyId
      }).then(() => {
        this.fetchList()
        this.dialogCopy = false
      })
    },
    handleCopyCancel() {
      this.dialogCopy = false
    },
    countValue(item) {
      return item && item.valueCounted ? item.valueCounted : (item ? 'NaN' : null)
    },
    localDateFromString(dateString) {
      return new Date(dateString).toLocaleString('sv').substr(0, 10)
    },
    localDateFromDate(date) {
      return date.toLocaleString('sv').substr(0, 10)
    },
    unitSaved(multiplier) {
      this.multiplier = multiplier
    },
    getMultipliedTemp() {
      const newTemp = Object.assign({}, this.temp)
      if (newTemp.value && Number.parseFloat(newTemp.value)) { newTemp.value = (Number.parseFloat(newTemp.value) * this.multiplier).toString() }
      return newTemp
    }
  }

}
</script>

<style scoped>

</style>
