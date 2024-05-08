import flet as ft

def test():
    return ft.Row(controls=[
        ft.Column(
            horizontal_alignment="stretch",
            controls=[
                ft.Card(content=ft.Container(ft.Text('meme', weight="bold"), padding=8)),
                ft.TextField(),
            ],
            expand=True,
        ),
    ],
    expand=True,)
