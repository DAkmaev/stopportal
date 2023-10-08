export async function getMoexHistory(tiker, from, to) {
  let offset = 0
  let result = []
  let isFinished = false

  while (!isFinished) {
    const url = `https://iss.moex.com/iss/history/engines/stock/markets/shares/securities/${tiker}.json?iss.json=extended&from=${from}&till=${to}&start=${offset}&limit=100&sort_column=TRADEDATE&sort_order=desc&lang=ru&iss.meta=off`
    const data = await fetch(url)
    const content = await data.json()

    const historyBlock = content.find(e => 'history' in e)
    result = result.concat(
      historyBlock['history'].filter(e => e.BOARDID === 'TQBR')
    )

    const cursor = historyBlock['history.cursor'][0]
    offset += cursor.PAGESIZE

    isFinished = cursor.TOTAL <= cursor.INDEX + cursor.PAGESIZE
  }

  return result
}

export async function getMoexSharesCount(tiker) {
  const url = `https://iss.moex.com/iss/securities/${tiker}.json?iss.meta=off&iss.json=extended`
  const data = await fetch(url)
  const content = await data.json()
  const descriptionBlock = content.find(e => 'description' in e)
  if (descriptionBlock && descriptionBlock.description && descriptionBlock.description.length > 0) {
    const sizeBlock = descriptionBlock.description.find(i => i.name === 'ISSUESIZE')
    return sizeBlock ? Number.parseInt(sizeBlock.value, 10) : null
  } else { return null }
}

export async function getMoexLotSize(tiker) {
  const url = `https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/${tiker}.jsonp?iss.meta=off&iss.only=securities`
  const data = await fetch(url)
  const mosLotSize = await data.json()
  const lotSize = mosLotSize.securities.data && mosLotSize.securities.data.length > 0 ? mosLotSize.securities.data[0][mosLotSize.securities.columns.indexOf('LOTSIZE')] : 0
  return lotSize
}

