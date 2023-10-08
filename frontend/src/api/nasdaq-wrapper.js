export default class NasdaqWrapper {
  getQuoteInfoByTiker(tiker) {
    return this.sendRespond(`https://api.nasdaq.com/api/quote/${tiker}/info?assetclass=stocks`)
  }
  async sendRespond(url) {
    const data = await fetch(url)
    const content = await data.json()
    return content
  }
}
