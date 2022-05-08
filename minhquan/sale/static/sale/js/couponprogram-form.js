$(function () {
  const rules = {
    product: JSON.parse(JSON.parse(document.getElementById('product_rules').textContent)),
    customer: JSON.parse(JSON.parse(document.getElementById('customer_rules').textContent)),
    order: JSON.parse(JSON.parse(document.getElementById('order_rules').textContent))
  }

  console.log('rules', rules)

  $('.rule-widget').on('change', function () {
    const model = $(this).data('model')
    const field = $(this).data('field')
    const operatorSource = $(this).data('operator-source')
    const valueSource = $(this).data('value-source')
    let operator = $(this).data('operator')
    let value = $(this).val()

    if (valueSource) {
      operator = $(this).val()
      value = $(`[name=${valueSource}]`).val()
    } else if (operatorSource) {
      operator = $(`[name=${operatorSource}]`).val()
      value = $(this).val()
    }

    const isChecked = $(this).is(':checked')
    const isCheckbox = $(this).hasClass('apply-checkbox')
    const $itemParent = $(this).parents('.accordion')

    if (!rules[model]) { rules[model] = {} }

    if ($itemParent.length) {
      if (!rules[model][field]) { rules[model][field] = {} }
      
      rules[model][field][operator] = value
      if (isCheckbox && !isChecked) {
        delete rules[model][field][operator]
      }

      const $ruleElement = $(`#id_rule_${model}`)
      $ruleElement.val(JSON.stringify(rules[model]))
    }
  })
})