'use strict'
import Result from './Result'
export default class MParser {
  constructor() {
    this.variables = {}
    // const  result = new Result("22+21")
  }

  setVariable(variableName, variableValue) {
    this.variables[variableName] = variableValue
  }

  getVariable(variableName) {
    if (!Object.keys(this.variables).includes(variableName)) {
      console.error(`Error: Try get unexists variable ${variableName}`)
      // return 0.0;
    }
    return this.variables[variableName]
  }

  Parse(s) {
    const result = this.PlusMinus(s.replace(/\s+/g, ''))
    if (result.rest !== '') {
      console.error("Error: can't full parse")
      console.error(`rest: ${result.rest}`)
    }
    return result.acc
  }

  PlusMinus(s) {
    let current = this.MulDiv(s)
    let acc = current.acc

    while (current.rest.length > 0) {
      if (!(current.rest[0] === '+' || current.rest[0] === '-')) break

      const sign = current.rest[0]
      const next = current.rest.substr(1)

      current = this.MulDiv(next)
      if (sign === '+') {
        acc += current.acc
      } else {
        acc -= current.acc
      }
    }
    return new Result(acc, current.rest)
  }

  Bracket(s) {
    const zeroChar = s[0]
    if (zeroChar === '(') {
      const r = this.PlusMinus(s.substr(1))
      if (r.rest !== '' && r.rest[0] === ')') {
        r.rest = r.rest.substr(1)
      } else {
        console.error('Error: not close bracket')
      }
      return r
    }
    return this.FunctionVariable(s)
  }

  FunctionVariable(s) {
    let f = ''
    let i = 0
    // ищем название функции или переменной
    // имя обязательно должна начинаться с буквы
    while (i < s.length && (/[A-Za-zА-Яа-я]/.test(s[i]) || /[0-9]/.test(s[i]) && i > 0)) {
      f = f + s[i]
      i++
    }
    if (f !== '') { // если что-нибудь нашли
      if (s.length > i && s[i] === '(') { // и следующий символ скобка значит - это функция
        const r = this.Bracket(s.substr(f.length))
        return this.processFunction(f, r)
      } else { // иначе - это переменная
        return new Result(this.getVariable(f), s.substr(f.length))
      }
    }
    return this.Num(s)
  }

  MulDiv(s) {
    let current = this.Bracket(s)
    let acc = current.acc
    while (current.rest.length > 0) {
      const sign = current.rest[0]
      if ((sign !== '*' && sign !== '/')) return current

      const next = current.rest.substr(1)
      const right = this.Bracket(next)

      if (sign === '*') {
        acc *= right.acc
      } else {
        acc /= right.acc
      }

      current = new Result(acc, right.rest)
    }

    return current
  }

  Num(s) {
    let i = 0
    let dot_cnt = 0
    let negative = false
    // число также может начинаться с минуса
    if (s[0] === '-') {
      negative = true
      s = s.substr(1)
    }
    // разрешаем только цифры и точку
    while (i < s.length && (/[0-9\.]/.test(s[i]))) {
      // но также проверям, что в числе может быть только одна точка!
      if (s[i] === '.' && ++dot_cnt > 1) {
        console.error("not valid number '" + s.substr(0, i + 1) + "'")
      }
      i++
    }
    if (i === 0) { // что-либо похожее на число мы не нашли
      console.error("can't get valid number in '" + s + "'")
    }

    let dPart = parseFloat(s.substr(0, i))
    if (negative) dPart = -dPart
    const restPart = s.substr(i)

    return new Result(dPart, restPart)
  }

  // Тут определяем все нашие функции, которыми мы можем пользоватся в формулах
  processFunction(func, r) {
    if (func === 'sin') {
      return new Result(Math.sin(r.acc), r.rest)
    } else if (func === 'cos') {
      return new Result(Math.cos(r.acc), r.rest)
    } else if (func === 'tan') {
      return new Result(Math.tan(r.acc), r.rest)
    } else {
      console.error(`function '${func}' is not defined`)
    }
    return r
  }
}
