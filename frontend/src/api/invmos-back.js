import store from '@/store'

function fillUrl(endpoint, params) {
  let url = `${process.env.VUE_APP_API_URL}/${endpoint}`
  if (params && Object.keys(params).length > 0) {
    url += '?'
    url += Object.keys(params)
      .filter(k => !!params[k])
      .map(k => `${k}=${params[k]}`)
      .join('&')
  }
  return url
}

async function requestWithBody(method, endpoint = '', body = {}, parseResponse = true, params = {}) {
  try {
    const authToken = store.state.token
    const url = fillUrl(endpoint, params)
    const headers = { 'Content-Type': 'application/json' }
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`
    }
    const data = await fetch(url, {
      method: method,
      mode: 'cors', // no-cors, *cors, same-origin
      headers: headers,
      redirect: 'follow', // manual, *follow, error
      body: JSON.stringify(body)
    })
    if (parseResponse) {
      return await data.json()
    }
    return true
  } catch (e) {
    console.error(e.message)
    throw new Error(`Exception during sendint request to ${endpoint}`)
  }
}

export async function sendFormData(endpoint = '', body = {}, parseResponse = true, params = {}) {
  const url = fillUrl(endpoint, params)
  const data = await fetch(url, {
    method: 'POST',
    mode: 'cors', // no-cors, *cors, same-origin
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    redirect: 'follow', // manual, *follow, error
    body: new URLSearchParams(body).toString()
  })
  if (!data.ok) {
    throw new Error(data.statusText)
  }
  if (parseResponse) {
    return await data.json()
  }
  return data
}

export async function getData(endpoint = '', params = {}, parseJsonResponse = true) {
  try {
    const authToken = store.state.token
    const url = fillUrl(endpoint, params)
    const headers = { 'Content-Type': 'application/json' }
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`
    }
    const response = await fetch(url, {
      method: 'GET',
      headers: headers
    })
    if (response.status !== 200) {
      console.error(response.statusMessage)
      throw new Error(`Error gettting data ${endpoint}, params: ${params}`)
    }
    return parseJsonResponse ? await response.json() : await response.text()
  } catch (e) {
    console.error(e)
    throw new Error(`Error gettting data ${endpoint}, params: ${params}, error: ${e.message}`)
  }
}

export async function postData(endpoint = '', body = {}, params = {}, parseResponse = true) {
  return requestWithBody('POST', endpoint, body, parseResponse, params)
}

export async function putData(endpoint = '', body = {}, params = {}, parseResponse = true) {
  return requestWithBody('PUT', endpoint, body, parseResponse, params)
}

export async function patchData(endpoint = '', body = {}, params = {}, parseResponse = true) {
  return requestWithBody('PATCH', endpoint, body, parseResponse, params)
}

export async function deleteData(endpoint = '', params = {}) {
  return requestWithBody('DELETE', endpoint, {}, false, params)
}

export async function getCategoriesSimple(type) {
  return await getData('categories-simple', {
    'type': type
  })
}

export async function getStrategies() {
  return await getData(endpoints.STRATEGIES, {})
}

export const endpoints = Object.freeze({
  BRIEFCASE: 'briefcase',
  BRIEFCASE_ITEMS: 'briefcase/items',
  BRIEFCASE_REGISTRY: 'briefcase/registry',
  COMPANIES: 'companies/',
  COMPANIES_CATEGORIES: 'companies/categories',
  COMPANIES_STRATEGIES: 'companies/strategies',
  DIVIDENDS: 'dividends',
  DIVIDENDS_DATA: 'dividends/data',
  DIVIDENDS_DOHODNOST: 'dividends/dohodnost',
  DIVIDENDS_OVERALL: 'dividends/overall',
  PRICES: 'prices',
  SYNC_LAST: 'sync/last',
  CATEGORIES: 'categories',
  CATEGORIES_SIMPLE: 'categories-simple',
  COEFFICIENTS: 'coefficients',
  COEFFICIENTS_VALUES: 'coefficients/values',
  COEFFICIENTS_VALUES_DATES: 'coefficients/values/dates',
  COEFFICIENTS_VALUES_COPY: 'coefficients/values/copy',
  RATINGS: 'ratings',
  RATINGS_BRIEFCASE: 'ratings/briefcases',
  RATINGS_COEFFICIENTS: 'ratings/coefficients',
  RATINGS_IMPULSE_GROW: 'ratings/impulse-grow',
  REPORTS: 'reports',
  REPORTS_COLUMNS: 'reports/columns',
  REPORTS_VALUES: 'reports/values',
  REPORTS_VALUE: 'reports/value',
  REPORTS_UNITS: 'reports/units',
  TA: 'ta/',
  STOPS: 'stops/',
  STRATEGIES: 'strategies/',
  STRATEGIES_MIH: 'strategies/mih',
  STRATEGIES_MIH_DETAILS: 'strategies/mih/details',
  LOGIN: 'login',
  ME: 'auth/me'
})
