$(function () {
  const rules = {
    product: JSON.parse(JSON.parse(document.getElementById('product_rules').textContent)),
    customer: JSON.parse(JSON.parse(document.getElementById('customer_rules').textContent)),
    order: JSON.parse(JSON.parse(document.getElementById('order_rules').textContent))
  }

  $(document).on('change', '#id_rule_product', function () {
    SERVICES.getProductsByRule({
      data: rules.product,
      success: function (response) {
        $('#ruleProductReflection table tbody').empty()
        if (!response.success) {
          $(`[id^=id_rule_product][id$=total]`).html(0)
        } else {
          const { result, fields } = response.data
          $('#id_rule_product_total').html(result.length)
          Object.keys(fields).forEach(function (field) {
            $(`#id_rule_product_${field}_total`).html(fields[field].length)
          })

          result.forEach(function (product, index) {
            $('#ruleProductReflection table tbody').append(`
              <tr>
                <td>${index + 1}</td>
                <td><img width="40" height="40" src="/media/${product.image}" alt="${product.name}"></td>
                <td>${product.name}</td>
              </tr>
            `)
          })
          
        }
      }
    })
  })

  $(document).on('change', '#id_rule_customer', function () {
    SERVICES.getCustomersByRule({
      data: rules.customer,
      success: function (response) {
        $('#ruleCustomerReflection table tbody').empty()
        if (!response.success) {
          $(`[id^=id_rule_customer][id$=total]`).html(0)
        } else {
          const { result, fields } = response.data
          $('#id_rule_customer_total').html(result.length)
          Object.keys(fields).forEach(function (field) {
            $(`#id_rule_customer_${field}_total`).html(fields[field].length)
          })

          result.forEach(function (customer, index) {
            $('#ruleCustomerReflection table tbody').append(`
              <tr>
                <td>${index + 1}</td>
                <td>${customer.full_name}</td>
                <td>${customer.email}</td>
                <td>${customer.phone}</td>
              </tr>
            `)
          })
        }
      }
    })
  })

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
      if (valueSource) { // change operator
        operator = $(this).val()
        value = $ruleItem.find(`[name=${valueSource}]`).val()
      } else if (operatorSource) { // change value
        operator = $ruleItem.find(`[name=${operatorSource}]`).val()
        value = $(this).val()
      }

      if ($ruleItem.attr('data-rule-widget') === 'number' || $ruleItem.attr('data-rule-widget') === 'date') {
        if (operator === 'range') {
          const valueFrom = $ruleItem.find(`[data-range=from]`).val()
          const valueTo = $ruleItem.find(`[data-range=to]`).val()
          value = [valueFrom, valueTo]
          $ruleItem.find('.range-input').removeClass('d-none')
          $ruleItem.find('.single-input').addClass('d-none')
        } else {
          $ruleItem.find('.range-input').addClass('d-none')
          $ruleItem.find('.single-input').removeClass('d-none')
        }
      }

      rules[model]['fields'][field]['lookups'][lookupIndex] = { [operator]: value }
    }

    const $ruleElement = $(`#id_rule_${model}`)
    $ruleElement.val(JSON.stringify(rules[model])).trigger('change')
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
    const lookupIndex =  $ruleItem.attr('data-order')
    const model = $(this).data('model')
    const field = $(this).data('field')
    rules[model]['fields'][field]['lookups'].splice(lookupIndex, 1)
    const $ruleElement = $(`#id_rule_${model}`)
    $ruleElement.val(JSON.stringify(rules[model])).trigger('change')
    $ruleItem.remove()
  })

  $('#total-coupon').on('change', function () {
    const totalFormsets = $(this).val()
    const code = $('#id_name').val().replaceAll(/\s/g,'-')
    const start_date = new Date($('#id_start_date').val()).toISOString().substring(0,10)
    const expired_date = new Date($('#id_expired_date').val()).toISOString().substring(0,10)
    addFormSet({
      formsetSelector: '.formset',
      total: parseInt(totalFormsets),
      initials: {
        code: function () { return code + Date.now() },
        start_date: start_date,
        expired_date: expired_date
      }
    })
  })

  $('.tab-label').on('change', function () {
    const tabId = $(this).val() || $(this).id
    $(this).parents('.tabs').find('.tab-content').hide()
    $(`.${tabId}`).show()
  })
})