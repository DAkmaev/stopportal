export const nest = (items, id = null, link = 'parent_id') =>
  items
    .filter(item => item[link] === id)
    .map(item => ({ ...item, children: nest(items, item.id) }))

export const flattenTree = (treeObj) => {
  const flatten = (children, level, parent) => {
    return children.reduce((res, item) => {
      res.push({ ...item, level: level || 1, parent_id: parent || null })
      return res.concat(flatten(item.children || [], (level || 1) + 1, item.id))
    }, [])
  }
  return flatten(treeObj).map(x => delete x.children && x)
}
