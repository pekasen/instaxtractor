# PlugIn-System Specification

This document shall serve as a specification document on what `instaxtractor`
expects to be registered with the `[tool.poetry.plugins.instaxtractor]`-entry point.

## 1. Plug-In-Loading

> All commands are loaded dynamically, including the standard plug-ins `instaxtractor` ships with. Thus, it relies heavily on the correct functioning of this entrypoint and explicitly checks wether the loaded plug-in is of the correct type.

If a registered plug-in does not match the expected `click.Command` type, an error is raised and `instaxloader` will terminate.

## 2. Plug-In Interface

As stated, all plug-ins must be a valid `click.Command`, additionally we follow the multi-command pipeline specification given in the `click` documentation. This means that a plug-in is not expected to have both arguments or options. Rather, it _must_ return a _processor_ function, which will be collected by the main application and called in the due process.

The processor function must adhear to the following interface: `processor(file: Dict[str, Any]) -> None`. Any additional arguments, e.g. from the `click.Command` should be past into the function beforehand. For example:

```python
@click.command()
@click.option("--skip-large", flag=True)
def example(skip_large):
    def processor(file, skip_large):
        # do something here, but if wished skip large entities
        pass

    return partial(processor, skip_large=skip_large)
```
