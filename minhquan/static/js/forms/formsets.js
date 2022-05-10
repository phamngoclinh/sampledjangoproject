const addFormSet = function ({
  formsetElement = null,
  formsetEmptyElement = null,
  formsetInlinesElement = null,
  formsetSelector = '.formset',
  formsetEmptySelector = '.formset-empty',
  formsetInlinesSelector = '.formset-inlines',
  total = 1
}) {
  $formset = formsetElement || $(formsetSelector)
  $formsetEmpty = formsetEmptyElement || $formset.find(formsetEmptySelector)
  $formsetInlines = formsetInlinesElement || $formset.find(formsetInlinesSelector)

  const $totalForms = $formset.find('[name$=TOTAL_FORMS]')
  const totalForms = parseInt($totalForms.val())
  console.log('totalForms', $totalForms, totalForms)

  if (total >= totalForms) {
    const subTotal = total - totalForms
    for (let i = 0; i < subTotal; i++) {
      const totalForms = parseInt($totalForms.val())
      const $newForm = $formsetEmpty.children().clone()
  
      const newTotalForms = totalForms
      const matchValue = '__prefix__'
      const match = new RegExp(matchValue, 'g')
      const replace = newTotalForms.toString()
  
      attrs = ['name', 'id', 'for', 'class']
      attrs.forEach(function (attr) {
        $newForm.find(`[${attr}*=${matchValue}]`).each(function (el) {
          let newAttr = $(this).attr(attr).replace(match, replace)
          $(this).attr(attr, newAttr)
        })
      })
  
      $newForm.html($newForm.html().replace(match, replace))
  
      $totalForms.val(newTotalForms + 1)
      $formsetInlines.append($newForm)
    }
  } else {
    $formsetInlines.children().each(function (index) {
      if (index >= total) {
        $(this).remove()
      }
    })
    $totalForms.val(total)
  }
}
