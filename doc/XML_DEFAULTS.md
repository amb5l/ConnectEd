# XML defaults

A saved file publishes the default of every omittable property, so a reader can recover every stored property from the XML alone. `worthy` still decides what the body may omit. It does not say what the omission means.

This applies to file save and load only. The clipboard keeps today's rule: an omitted attribute is the constructor default, and paste does not read a preamble.

## Defaults

`Defaults` is the first child of the diagram element on a full-scene save. It holds one empty element per tag that appears in the file. That element is the defaults for the tag. Every attribute on it is a default, written with `val2str`, the same encoding as a live item.

```xml
<Defaults>
  <Port Rotation="0" MirrorH="False" MirrorV="False" Comment=""/>
  <Label Visible="True" Width="-1" Height="-1" Line_Color="None" Pad_Left="0"/>
</Defaults>
```

`Name`, `Dir`, `X`, and `Y` are absent, and every `Port` in the body writes them. `Name` and `Dir` have no `worthy` predicate. `X` and `Y` are the port's position, so they are written even at the origin; the current `worthy` check that drops `(0, 0)` does not apply to them. `Comment=""` is the empty string, the value omitted when a port has no comment. `Line_Color="None"` is the stored inherit value (`val2str(None)`), not the theme color in force at save time. Applying the theme color would freeze it onto the item.

An attribute that is not in the defaults for its tag has no default. The body is the only place its value appears. `ID` is such an attribute: it is absent from the defaults and appears on every netlist element.

Child items are not nested in a defaults element. A `Label` inside a port takes its defaults from the `Label` element. The writer emits attributes only, and it does not pass them through `worthy`.

## Reading an element

Start from the defaults for that tag, then apply the element's own attributes.

- The attribute is in the defaults and missing on the element. Use the default value.
- The attribute is in both. Use the element.
- The attribute is not in the defaults. It must be written on the element. If it is missing, the file is incomplete. Do not invent a value.

A custom property is the third case, only for the instances that own it. It is not in the defaults, so each of those instances writes it. Other instances of the tag do not carry it.

A file with no `Defaults` section loads as it does today: construct the item, then apply the attributes that are present.

## Survey, then write

`QXmlStreamWriter` is forward only, and the defaults have to precede the body. Saving a full scene walks the items twice and writes once.

The survey groups items by `xmlTag()`. For each property, it records the stored values (`value(raw=True)`) on the instances where `worthy()` is false. The attribute joins the defaults only when every one of those values is the same. The body then omits the attribute wherever the instance has that value.

When the omitted values differ, the attribute stays out of the defaults and every instance writes it. Width joins the defaults as `-1` when every omitted width is `-1`. Two different omitted widths leave `Width` out of the defaults.

A property with no `worthy` predicate is always worthy, so the survey never gives it a default. Every instance writes it. `X` and `Y` are required even though `worthy` is false at the origin: the survey does not record them, and the body always writes them.

The write pass emits `Defaults`, then the body. Body omission uses the defaults, not the `worthy` lambdas. Omit an attribute only when it equals the default value. Every other property attribute is written.

## Load

Read `Defaults` before the items. For each element, apply the defaults, then overlay the element's attributes. Honor the file when a default disagrees with the absent value implied by the current `worthy` predicate, and log a warning. Warn, and do not invent a value, when an instance omits an attribute that the defaults do not carry.

`copyXml` and `pasteXml` are unchanged. A copied selection is not a document: three ports that happen to share a rotation do not publish that rotation as a default, and an omitted line color still means inherit, so a paste into another sheet follows the destination theme.

## Work order

1. Survey full-scene items by tag. Record an attribute in the defaults only when every unworthy stored value is identical.
2. Write `Defaults` as the first child of the diagram element. One empty element per tag, every recorded attribute set with `val2str`.
3. Write the body from those defaults. Omit an attribute only when it equals the default value. Always write attributes the defaults do not carry.
4. On load, apply the defaults first and overlay element attributes. A missing `Defaults` section keeps the current load path. Warn when a default disagrees with the code, and warn when a required attribute is absent.
5. Leave the clipboard path alone.
