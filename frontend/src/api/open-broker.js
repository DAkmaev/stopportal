export async function getDividends(tiker, from, to) {
  let offset = 0
  const count = 100
  let result = []
  let isFinished = false

  while (!isFinished) {
    const url = `http://api.open-broker.ru/data/v2.0/corporate_events/dividends?date_from=${from}&rowsOffset=${offset}&date_to=${to}&rowsCount=${count}&orderBy=FixingDate-&status=A&instrument_Id=&search_text=${tiker}`
    const data = await fetch(url, {
      mode: 'no-cors'
    })
    const content = await data.json()

    result = result.concat(content.Dividends)
    offset += count

    isFinished = content.Dividends.length === 0
  }

  return result
}
