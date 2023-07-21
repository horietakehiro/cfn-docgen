from typing import Any, Callable, TypeVar

_FuncT = TypeVar('_FuncT', bound=Callable[..., Any])
_VT = TypeVar('_VT')

def register_type(**kwargs: _VT) -> None: ... # type: ignore
def given(step_text: str) -> Callable[[_FuncT], _FuncT]: ...
def when(step_text: str) -> Callable[[_FuncT], _FuncT]: ...
def then(step_text: str) -> Callable[[_FuncT], _FuncT]: ...


