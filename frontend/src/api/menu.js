const Menu = [
  {
    icon: 'mdi-file-tree',
    'icon-alt': 'mdi-file-tree',
    title: 'Справочники',
    model: false,
    children: [
      // { title: 'Статьи баланса', name: 'catalogBalance' },
      // { title: 'Статьи ПиУ', name: 'catalogPiu' },
      // { title: 'Статьи ДДС', name: 'catalogDds' },
      // { title: 'Отрасли', name: 'catalogOtrasli' },
      // { title: 'Коэффициенты', name: 'coefficients' }
      { title: 'Стратегии', name: 'strategies' }
    ]
  },
  { icon: 'mdi-factory', title: 'Компании', name: 'companies' },
  // { icon: 'mdi-currency-rub', title: 'Цены', name: 'prices' },
  // { icon: 'mdi-human-pregnant', title: 'Дивиденды', name: 'dividends' },
  // { icon: 'mdi-billboard', title: 'Отчетность', name: 'reports' },
  // {
  //   icon: 'mdi-align-horizontal-left',
  //   'icon-alt': 'mdi-align-horizontal-left',
  //   title: 'Рейтинги',
  //   name: 'ratings',
  //   children: [
  //     { title: 'По дивидендам', name: 'ratingDividends' },
  //     { title: 'Дивидендная доходность', name: 'ratingDividendsDohod' },
  //     { title: 'Импульс роста', name: 'ratingImpulseGrow' },
  //     { title: 'Долговая нагрузка', name: 'ratingDebt' },
  //     { title: 'Свободный денежный поток', name: 'ratingFreeMoneyFlow' },
  //     { title: 'Сводный рейтинг', name: 'ratingSummary' },
  //     { title: 'Формирование портфеля', name: 'ratingBriefcase' }
  //   ]
  // },
  { icon: 'mdi-bag-checked', title: 'Портфель', name: 'briefcase' }
  // { icon: 'mdi-bag-checked', title: 'Мих стратегия', name: 'strategyMih' }
]
// reorder menu
Menu.forEach(item => {
  if (item.children) {
    item.children.sort((x, y) => {
      const textA = x.title.toUpperCase()
      const textB = y.title.toUpperCase()
      return textA < textB ? -1 : textA > textB ? 1 : 0
    })
  }
})

export default Menu
