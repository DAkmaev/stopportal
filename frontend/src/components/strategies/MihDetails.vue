<template>
  <v-container fluid>
    <v-row class="justify" />
    <v-row>
      <v-col cols="10">
        <v-data-table
          :headers="headers"
          :items="list"
          :disable-pagination="true"
          :hide-default-footer="true"
          dense
        >
          <template v-slot:item="{item}">
            <tr>
              <td v-for="(col, columnIndex) in headers" :key="columnIndex">
                <div v-if="col.value === 'type'">{{ types[item.type] }}</div>
                <div
                  v-else-if="[
                    'support',
                    'resistance',
                    'support_avg',
                    'resistance_avg',
                    'signal_buy',
                    'risk_level',
                    'meaning_trading_volume'
                  ].includes(col.value)"
                ><div align="center">
                  <v-edit-dialog
                    :return-value.sync="item[col.value]"
                    @save="saveMihData(item)"
                  >{{ item[col.value] }}
                    <template v-slot:input>
                      <v-text-field
                        v-model="item[col.value]"
                        label="Изменить"
                        single-line
                        clearable
                      />
                    </template>
                  </v-edit-dialog>
                  <div
                    v-if="item[col.value] && [
                      'support',
                      'resistance',
                      'signal_buy',
                      'risk_level'
                    ].includes(col.value)"
                  >
                    <v-btn
                      x-small
                      icon
                      :color="strategy[col.value + '_id'] === item.id ? 'green' : 'gray'"
                      @click="changeStrategyDefault(strategy.id, item.id, col.value + '_id')"
                    >
                      <v-icon>mdi-star</v-icon>
                    </v-btn>
                  </div>
                </div>
                </div>
                <div v-else-if="['trend', 'trend_phase', 'volatility'].includes(col.value)">
                  <v-edit-dialog
                    :return-value.sync="item[col.value]"
                    @save="saveMihData(item)"
                  >
                    {{ catalogsKeyValue[col.value][item[col.value]] }}
                    <template v-slot:input>
                      <v-select
                        v-model="item[col.value]"
                        :items="catalogs[col.value]"
                        item-text="text"
                        item-value="id"
                      />
                    </template>
                  </v-edit-dialog>
                </div>
              </td>
            </tr>
          </template>
        </v-data-table>
      </v-col>
      <v-col cols="2" align="end">
        <v-textarea
          v-model="strategy.decision"
          outlined
          auto-grow
          dense
          label="Что делаем то?"
          rows="3"
          @input="decisionDisabled = false"
        />
        <v-btn
          x-large
          color="success"
          :disabled.sync="decisionDisabled"
          @click="updateStrategy"
        >Сохранить</v-btn>
      </v-col>
    </v-row>
    <v-divider />
    <v-row>
      <v-col offset="4" cols="6">
        <mih-calculation :strategy="strategy" @mih-item-changed="decisionDisabled = false" />
      </v-col>
      <v-col cols="2">
        <v-text-field
          v-model="strategy.multiply"
          label="Коэффициент"
          outlined
          dense
          @input="decisionDisabled = false"
        />
        <v-text-field
          v-model="strategy.budget"
          label="Бюджет"
          outlined
          dense
          @input="decisionDisabled = false"
        />
      </v-col>
    </v-row>

    <!--    <v-row>
      <v-col offset="2" cols="8">
        <v-card
          elevation="2"
        >
          <div>
            <apexchart
              v-if="this.series.length > 0"
              type="candlestick"
              :options="chartOptions"
              :series="series"
            />
          </div>
        </v-card>
      </v-col>
    </v-row>-->
  </v-container>
</template>

<script>
import MihCalculation from '@/components/strategies/MihCalculation'
import { endpoints, getData, putData } from '@/api/invmos-back'
/* import apexchart from 'vue-apexcharts'*/
export default {
  name: 'MihDetails',
  components: { MihCalculation },
  /* components: { apexchart },*/
  props: {
    strategy: {
      type: Object,
      default: undefined
    }
  },
  data() {
    return {
      decisionDisabled: true,
      list: [],
      catalogs: {
        trend: [
          { id: 'down', text: 'падающая' },
          { id: 'grow', text: 'растущая' },
          { id: 'outset', text: 'боковик' }

        ],
        trend_phase: [
          { id: 'outset', text: 'боковик' },
          { id: 'correction', text: 'коррекция' },
          { id: 'correction_grow', text: 'коррекция или начало роста' },
          { id: 'grow_outset', text: 'рост в боковике' },
          { id: 'down_outset', text: 'падение в боковике' },
          { id: 'correction_down', text: 'коррекция или начало падения' },
          { id: 'grow', text: 'растущая' },
          { id: 'down', text: 'падающая' }
        ],
        volatility: [
          { id: 'low', text: 'низкая' },
          { id: 'avg', text: 'средняя' },
          { id: 'high', text: 'высокая' }
        ]
      },
      types: {
        'day': 'День',
        'week': 'Неделя',
        'month': 'Месяц'
      },
      headers: [
        { text: 'Тип графика', value: 'type', sortable: false, class: 'mih-details-header' },
        { text: 'Тенденция', value: 'trend', class: 'mih-details-header' },
        { text: 'Фаза тенденции', value: 'trend_phase', class: 'mih-details-header' },
        { text: 'Основное сопротивление', value: 'resistance', align: 'center', class: 'mih-details-header' },
        { text: 'Основная поддержка', value: 'support', align: 'center', class: 'mih-details-header' },
        { text: 'Промежуточная поддержка', value: 'support_avg', align: 'center', class: 'mih-details-header' },
        { text: 'Промежуточное сопротивление', value: 'resistance_avg', align: 'center', class: 'mih-details-header' },
        { text: 'Где сигнал на покупку', value: 'signal_buy', align: 'center', class: 'mih-details-header' },
        { text: 'Где уровень риска', value: 'risk_level', align: 'center', class: 'mih-details-header' },
        { text: 'Что говорят объемы торгов', value: 'meaning_trading_volume', class: 'mih-details-header' },
        { text: 'Какая волатильность', value: 'volatility', class: 'mih-details-header' }
      ]
      /* series: [],
      chartOptions: {
        chart: {
          type: 'candlestick',
          zoom: {
            enabled: true,
            type: 'x',
            autoScaleYaxis: true,
            zoomedArea: {
              fill: {
                color: '#90CAF9',
                opacity: 0.9
              },
              stroke: {
                color: '#0D47A1',
                opacity: 0.9,
                width: 1
              }
            }
          },
          animations: {
            enabled: false,
            animateGradually: {
              enabled: false
            },
            dynamicAnimation: {
              enabled: false
            }
          }
        },
        annotations: {
          xaxis: [
            {
              borderColor: '#00E396',
              label: {
                borderColor: '#00E396',
                style: {
                  fontSize: '12px',
                  color: '#fff',
                  background: '#00E396'
                },
                orientation: 'horizontal',
                offsetY: 7,
                text: 'Annotation Test'
              }
            }
          ]
        },
        tooltip: {
          enabled: true
        },
        yaxis: {
          tooltip: {
            enabled: true
          },
          showForNullSeries: false
        },
        xaxis: {
          type: 'datetime'
          /!* type: 'category',
          labels: {
            formatter: function(val) {
              //const c = new Date()
              return val//.toISOString()
            }
          }*!/
        }
      }*/
    }
  },
  computed: {
    catalogsKeyValue: function() {
      return Object.entries(this.catalogs).reduce((res, catalog) => {
        const [name, values] = catalog
        res[name] = values.reduce((vals, k) => {
          vals[k.id] = k.text
          return vals
        }, {})
        return res
      }, {})
    }
  },
  watch: {
    strategy: function() {
      this.fetchList()
    }
  },
  created() {
    this.fetchList()
  },
  methods: {
    saveMihData(item) {
      putData(endpoints.STRATEGIES_MIH_DETAILS, item, false, { strategyId: this.strategy.id, companyId: this.strategy.company_id })
      this.$emit('mih-item-refresh')
    },
    updateStrategy() {
      this.$emit('mih-item-update')
      this.decisionDisabled = true
    },
    async fetchList() {
      if (this.strategy) {
        const data = this.strategy.id ? await getData(endpoints.STRATEGIES_MIH_DETAILS, { strategyId: this.strategy.id }) : null
        this.list = ['month', 'week', 'day'].reduce((res, c) => {
          res.push(data && data.some(e => e.type === c) ? data.find(d => d.type === c) : {
            'id': null,
            'type': c,
            'resistance': null,
            'resistance_avg': null,
            'support': null,
            'support_avg': null,
            'signal_buy': null,
            'risk_level': null,
            'trend': null,
            'trend_phase': null,
            'volatility': null,
            'meaning_trading_volume': null
          })
          /* this.fetchCandleData()*/
          return res
        }, [])
      } else {
        this.series = []
        this.list = []
      }
    },
    changeStrategyDefault(strategyId, detailsId, column) {
      const value = this.strategy[column] === detailsId ? null : detailsId
      this.$emit('mih-item-default-update', strategyId, value, column)
    }/*,
    async fetchCandleData() {
      const prices = await queryAllPrices(undefined, undefined, this.strategy.company_id)
      const data = prices.map(p => { // getData(prices).map(p => {
        return ({
          x: p.date,
          y: [p.open, p.high, p.low, p.close]
        })
      })

      this.series = [{
        name: 'candle',
        data: data
      }]
    }*/
  }
}
</script>

<style scoped>
.mih-details-header {
  background-color: #eee4c6;
}
</style>

