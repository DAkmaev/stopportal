'use strict'
import TwelveWrapper from '@/api/twelve-wrapper'
import { getMoexSharesCount, getMoexLotSize, getMoexHistory } from '@/api/moex'
import { getData, postData, endpoints } from '@/api/invmos-back'

export default class PriceSynchronizer {
  constructor() {
    this.defaultTimeOffset = 31556926000
  }
  async sync(ids = null) {
    const lastDate = ids ? new Date(Date.now() - this.defaultTimeOffset).toLocaleString('sv').substr(0, 10) : await getData(endpoints.SYNC_LAST, { id: 1 }, false)
    const nowDate = new Date(Date.now()).toLocaleString('sv').substr(0, 10)
    const companies = await getData('companies', ids ? { ids: ids.join(',') } : {})
    const companiesMoex = companies.filter(c => c.currency === 'RUB')
    const companiesNyse = companies.filter(c => c.currency !== 'RUB')
    await Promise.all(
      companiesMoex.map(async c => {
        return this.syncMoexPrices(c.tiker, lastDate, nowDate, c.id, !ids)
      }).concat(this.syncNysePricesBulk(companiesNyse, lastDate, !ids))
    )
  }
  async syncMoexPrices(tiker, dateFrom, dateTo, companyId, updateLastDate) {
    const [issueSize, lotSize, histData] = await Promise.all([
      getMoexSharesCount(tiker),
      getMoexLotSize(tiker),
      getMoexHistory(tiker, dateFrom, dateTo)
    ])
    return postData('prices', histData, false, {
      issueSize: issueSize,
      lotSize: lotSize,
      companyId: companyId,
      updateLastDate: updateLastDate,
      type: 'moex'
    })
  }
  async syncNysePricesBulk(companies, dateFrom, updateLastDate) {
    if (companies.length === 1) { return this.syncNysePrices(companies[0].tiker, dateFrom, companies[0].id, updateLastDate) }

    const data = await this.getNysePriceData(companies.map(c => c.tiker), dateFrom)
    const tasks = []
    companies.forEach(c => {
      if (data[c.tiker].status === 'ok') {
        const syncFun = async(prices, tiker, companyId) => {
          // const quoteData = await new NasdaqWrapper().getQuoteInfoByTiker(tiker)
          const marketCap = null// Number.parseFloat(quoteData.data.keyStats.MarketCap.value.replace(',', ''))
          return postData('prices', prices, false, {
            capitalization: marketCap,
            companyId: companyId,
            updateLastDate: updateLastDate,
            type: 'nyse'
          })
        }
        tasks.push(syncFun(data[c.tiker].values, c.tiker, c.id))
      }
    })

    Promise.all(tasks).then(console.log('Inserted data', data))
  }
  async syncNysePrices(tiker, dateFrom, companyId, updateLastDate) {
    const data = await this.getNysePriceData([tiker], dateFrom)
    // const quoteData = await new NasdaqWrapper().getQuoteInfoByTiker(tiker)
    //
    const marketCap = null // Number.parseFloat(quoteData.data.keyStats.MarketCap.value.replace(',', ''))
    return postData('prices', data.values, false, {
      capitalization: marketCap,
      companyId: companyId,
      updateLastDate: updateLastDate,
      type: 'nyse'
    })
  }

  async getNysePriceData(tikers, dateFrom) {
    const twelve = new TwelveWrapper()
    const data = await twelve.getDataByTikers(tikers, dateFrom)
    return data
  }
}
