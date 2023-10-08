export default class TwelveWrapper {
  constructor() {
    const twelvedata = require('twelvedata')
    this.config = {
      key: '36faf57c880c4bf79953c2cd80456c59'
    }
    this.client = twelvedata(this.config)
  }

  async getDataByTikers(tikers, start_date) {
    const params = {
      symbol: tikers.join(','),
      interval: '1day'
    }
    if (start_date) { params['start_date'] = start_date }

    const data = await this.client.timeSeries(params)
    return data
  }
}
