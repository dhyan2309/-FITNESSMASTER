from django import template


register = template.Library()


@register.filter
def package_features(description):
    if not description:
        return []

    features = []
    for line in str(description).splitlines():
        feature = line.strip()
        if feature.startswith("\u2705"):
            feature = feature[1:].strip()
        if feature:
            features.append(feature)
    return features


@register.simple_tag(takes_context=True)
def convert_price(context, amount):
    """Converts INR amount to USD if needed and adds currency symbol."""
    if amount is None:
        return ""
    
    curr = context.get('currency', 'INR')
    usd_rate = context.get('usd_rate', 83.5)
    
    try:
        amount = float(amount)
        if curr == 'USD':
            converted = amount / usd_rate
            return f"${converted:,.2f}"
        else:
            return f"₹{amount:,.2f}"
    except (ValueError, TypeError):
        return amount
