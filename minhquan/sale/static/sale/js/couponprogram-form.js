$(function () {
  const rules = {
    product: JSON.parse(JSON.parse(document.getElementById('product_rules').textContent)),
    customer: JSON.parse(JSON.parse(document.getElementById('customer_rules').textContent)),
    order: JSON.parse(JSON.parse(document.getElementById('order_rules').textContent))
  }

  $(document).on('change', '.rule-widget', function () {
    const model = $(this).data('model')
    const field = $(this).data('field')
    const extraKey = $(this).data('extra')
    const operatorSource = $(this).data('operator-source')
    const valueSource = $(this).data('value-source')
    let operator = $(this).data('operator')
    let value = $(this).val()

    const isChecked = $(this).is(':checked')
    const isCheckbox = $(this).hasClass('apply-checkbox')

    if (isCheckbox && !isChecked) {
      value = false
    } else if (isCheckbox && isChecked) {
      value = true
    }

    if (model && !rules[model]) { rules[model] = { 'fields': {}, 'extra': {} } }
    if (field && !rules[model]['fields'][field]) { rules[model]['fields'][field] = { 'lookups': [], 'extra': {} } }

    if (extraKey) {
      // extra
      if (field) {
        rules[model]['fields'][field]['extra'][extraKey] = value
      } else {
        rules[model]['extra'][extraKey] = value
      }
    } else {
      // lookups
      $ruleItem = $(this).parents('.rule_item')
      const lookupIndex =  $ruleItem.attr('data-order')
      if (valueSource) {
        operator = $(this).val()
        value = $ruleItem.find(`[name=${valueSource}]`).val()
      } else if (operatorSource) {
        operator = $ruleItem.find(`[name=${operatorSource}]`).val()
        value = $(this).val()
      }
      rules[model]['fields'][field]['lookups'][lookupIndex] = { [operator]: value }
    }

    const $ruleElement = $(`#id_rule_${model}`)
    $ruleElement.val(JSON.stringify(rules[model]))
  })

  $('.add_more_rule').on('click', function () {
    $collapse = $(this).parents('.accordion-collapse')
    $ruleItem = $collapse.find('.rule_item').last()

    $newRuleItem = $ruleItem.clone()
    // reset
    const latestOrder = parseInt($newRuleItem.data('order'))
    $newRuleItem.find('select').prop('selectedIndex', 0)
    $newRuleItem.find('input').prop('value', '')
    $newRuleItem.attr('data-order', latestOrder + 1)

    $newRuleItem.appendTo($collapse)
  })

  $(document).on('click', '.remove_rule_item', function () {
    $ruleItem = $(this).parents('.rule_item')
    $ruleItem.remove()
  })
})