<template>
  <v-simple-table dense>
    <template v-slot:default>
      <!--      <thead>
        <tr class="briefcase-main-column" align="center" colspan="4">Расчет покупки акций и риска</tr>
      </thead>-->
      <tbody>
        <tr>
          <td><span>Количество акций в лоте</span></td>
          <td>{{ lot_size }}</td>
          <td><span>Количество лотов</span></td>
          <td>
            <v-text-field
              v-model="strategy.lots"
              solo
              dense
              style="width: 50%"
              @input="changeStrategy"
            />
          </td>
          <td />
          <td />
        </tr>
        <tr>
          <td><span>Цена покупки лота</span></td>
          <td>
            <v-text-field
              v-model="strategy.lot_price"
              solo
              dense
              style="width: 50%"
              @input="changeStrategy"
            />
          </td>
          <td><span>Цена покупки</span></td>
          <td>{{ to_buy_price }}</td>
          <td><span>Бюджет</span></td>
          <td>{{ budget }}</td>
        </tr>
        <tr>
          <td><span>Цена стопа лота</span></td>
          <td>{{ lot_stop_price }}</td>
          <td><span>Цена стопа</span></td>
          <td>{{ stop_price }}</td>
          <td><span>Риск от бюджета</span></td>
          <td>{{ budget_risk }}</td>
        </tr>
        <tr>
          <td><span>Риск</span></td>
          <td>{{ lot_risk }}</td>
          <td><span>Риск</span></td>
          <td>{{ risk }}</td>
          <td />
          <td />
        </tr>
        <tr>
          <td><span>% риска</span></td>
          <td>{{ lot_risk_perc }}%</td>
          <td><span>% риска</span></td>
          <td>{{ risk_perc }}%</td>
          <td />
          <td />
        </tr>
      </tbody>
    </template>
  </v-simple-table>
</template>

<script>
export default {
  name: 'MihCalculation',
  props: {
    strategy: {
      type: Object,
      default: undefined,
      mandatory: true
    }
  },
  data() {
    return {
      // lots: 1
    }
  },
  computed: {
    lot_size: function() {
      return this.strategy && this.strategy.lot_size ? this.strategy.lot_size : 1
    },
    budget: function() {
      return this.strategy && this.strategy.budget ? this.strategy.budget : 0
    },
    /* lots: function (){
      return this.strategy && this.strategy.lots ? this.strategy.lots : 1
    },*/
    /* lot_price: function() {
      return this.strategy ? this.multiplyValue(this.strategy.signal_buy, this.strategy.multiply) : null
    },*/
    lot_stop_price: function() {
      return this.strategy ? this.multiplyValue(this.strategy.risk_level, this.strategy.multiply, true) : null
    },
    to_buy_price: function() {
      return this.strategy.lot_price ? this.strategy.lot_price * this.strategy.lots : null
    },
    stop_price: function() {
      return this.lot_stop_price ? this.lot_stop_price * this.strategy.lots : null
    },
    lot_risk: function() {
      return this.strategy.lot_price && this.lot_stop_price ? Math.round((this.lot_stop_price - this.strategy.lot_price) * 100, 2) / 100 : null
    },
    risk: function() {
      return this.to_buy_price && this.stop_price ? Math.round((this.stop_price - this.to_buy_price) * 100, 2) / 100 : null
    },
    lot_risk_perc: function() {
      return this.lot_risk && this.strategy.lot_price ? Math.round((this.lot_risk / this.strategy.lot_price) * 10000, 2) / 100 : null
    },
    risk_perc: function() {
      return this.risk && this.to_buy_price ? Math.round((this.risk / this.to_buy_price) * 10000, 2) / 100 : null
    },
    budget_risk: function() {
      return this.risk && this.budget ? Math.round((this.risk / this.budget) * 10000, 2) / 100 : null
    }
  },
  methods: {
    multiplyValue(val, multiply, negative = false) {
      const mult = multiply ? (negative ? multiply * -1 : multiply) : null
      return val ? (mult ? Math.round((val * mult / 100 + val) * 100, 2) / 100 : val) : null
    },
    changeStrategy() {
      this.$emit('mih-item-changed')
    }
  }
}
</script>

<style>
.briefcase-main-column {
  background-color: #eee4c6;
}
</style>
