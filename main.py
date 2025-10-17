import os
import shutil

from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup, VerticalScroll
from libGenerator import *
from textual.widgets import Label, Header, Footer, Button, Input, Static, Checkbox

arguments = {"kotlin": False,
             "mojang_mappings": False,
             "datagen": False,
             "split_client_and_common_sources": False,
             "remove_license": True}

def generate():
    authors = arguments["authors"].split(" ")
    contact = {"homepage": arguments["homepage"], "sources": arguments["mod_source"]}
    generator = Generator(authors=authors,
                          contact=contact,
                          description=arguments["description"],
                          project_license=arguments["project_license"],
                          license_full_name=arguments["license_fullname"],
                          mod_name=arguments["mod_name"],
                          mod_id=arguments["mod_id"],
                          mod_version=arguments["mod_version"],
                          package_name=arguments["package_name"],
                          kotlin=arguments["kotlin"],
                          mojang_mappings=arguments["mojang_mappings"],
                          datagen=arguments["datagen"],
                          split_client_and_common_sources=arguments["split_client_and_common_sources"],
                          remove_license=arguments["remove_license"]
                          )
    status = 0
    while status == 0:
        status = download_file("https://github.com/Fallen-Breath/fabric-mod-template/archive/refs/heads/master.zip","template.zip")
    unzip("template.zip")
    project_dir = os.getcwd()
    os.chdir("template")
    generator.rename_main_folder("fabric-mod-template-master")
    source_dir = generator.get_src_absolute_path()
    generator.chdir()
    generator.remove_file()
    generator.rebuild_package(generator.get_src_absolute_path(), generator.parse_package_name())
    os.chdir(project_dir)
    pack(arguments["file_path"]+os.path.sep+arguments["mod_id"]+"-template.zip",source_dir)
    shutil.rmtree(project_dir+os.path.sep+"template")

class ModNameArgumentInput(VerticalGroup):
    def compose(self) -> ComposeResult:
        yield Label("Mod Name", id="modname")
        yield Input(placeholder="Choose a name for your new mod.", id="modname_input")
    def on_input_changed(self, event: Input.Changed) -> None:
        arguments["mod_name"] = event.value

class ModIDArgumentInput(VerticalGroup):
    def compose(self) -> ComposeResult:
        yield Label("Mod ID", id="modid")
        yield Input(placeholder="Enter the mod ID you wish to use for your mod.", id="modid_input")
    def on_input_changed(self, event: Input.Changed) -> None:
        arguments["mod_id"] = event.value

class PackageNameArgumentInput(VerticalGroup):
    def compose(self) -> ComposeResult:
        yield Label("Package Name", id="packagename")
        yield Input(placeholder="Choose a unique package name for your new mod.", id="packagename_input")
    def on_input_changed(self, event: Input.Changed) -> None:
        arguments["package_name"] = event.value

class ModVersionArgumentInput(VerticalGroup):
    def compose(self) -> ComposeResult:
        yield Label("Mod Version", id="modversion")
        yield Input(placeholder="Enter the starting version you wish to release for your new mod.", id="modversion_input")
    def on_input_changed(self, event: Input.Changed) -> None:
        arguments["mod_version"] = event.value

class DescriptionArgumentInput(VerticalGroup):
    def compose(self) -> ComposeResult:
        yield Label("Description", id="description")
        yield Input(placeholder="Enter the description of your new mod.", id="description_input")
    def on_input_changed(self, event: Input.Changed) -> None:
        arguments["description"] = event.value

class ProjectLicenseArgumentInput(VerticalGroup):
    def compose(self) -> ComposeResult:
        yield Label("License Abbreviation", id="projectlicense")
        yield Input(placeholder="Enter the license abbreviation of your new mod.", id="projectlicense_input")
    def on_input_changed(self, event: Input.Changed) -> None:
        arguments["project_license"] = event.value

class LicenseFullNameArgumentInput(VerticalGroup):
    def compose(self) -> ComposeResult:
        yield Label("License Full Name", id="licensefullname")
        yield Input(placeholder="Enter the full name of your mod license.", id="license_fullname_input")
    def on_input_changed(self, event: Input.Changed) -> None:
        arguments["license_fullname"] = event.value

class AuthorsArgumentInput(VerticalGroup):
    def compose(self) -> ComposeResult:
        yield Label("Authors", id="authors")
        yield Input(placeholder="Enter all the contributors' name and separate them with spaces.", id="authors_input")
    def on_input_changed(self, event: Input.Changed) -> None:
        arguments["authors"] = event.value

class HomePageArgumentInput(VerticalGroup):
    def compose(self) -> ComposeResult:
        yield Label("Home Page", id="homepage")
        yield Input(placeholder="Enter the URL of your new mod's homepage.", id="homepage_input")
    def on_input_changed(self, event: Input.Changed) -> None:
        arguments["homepage"] = event.value

class ModSourceArgumentInput(VerticalGroup):
    def compose(self) -> ComposeResult:
        yield Label("Mod Source", id="modsource")
        yield Input(placeholder="Enter the URL of the source code repository for your new mod.", id="modsource_input")
    def on_input_changed(self, event: Input.Changed) -> None:
        arguments["mod_source"] = event.value

class AdvancedOptionsArgumentSelect(VerticalGroup):
    def compose(self) -> ComposeResult:
        yield Checkbox("[b]Kotlin Programming Language[/b]", id="kotlincheck")
        yield Checkbox("[b]Mojang Mappings[/b]", id="mojangcheck")
        yield Checkbox("[b]Data Generation[/b]", id="datagencheck")
        yield Checkbox("[b]Split Client and Common Sources[/b]", id="splitcheck")
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        checkbox_id = event.checkbox.id
        checked = event.value
        if checkbox_id == "kotlincheck":
            arguments["kotlin"] = checked
        elif checkbox_id == "mojangcheck":
            arguments["mojang_mappings"] = checked
        elif checkbox_id == "datagencheck":
            arguments["datagen"] = checked
        else:
            arguments["split_client_and_common_sources"] = checked


class AdvancedOptionsInstruction(VerticalGroup):
    def compose(self) -> ComposeResult:
        yield Static(
            "* Kotlin is a alternative programming language that can be used to develop mods. The Fabric Kotlin "
            "language adapter is used to enable support for creating Fabric Kotlin mods.\n"
            "* Use Mojang's official mappings rather than Yarn. Note that Mojang's mappings come with a usable yet "
            "more restrictive license than Yarn. Use them at your own risk.\n"
            "* This option configures the Fabric Data Generation API in your mod. This allows you to generate "
            "resources such as recipes from code at build time.\n"
            "* A common source of server crashes comes from calling client only code when installed on a server. This "
            "option configures your mod to be built from two source sets, client and main. This enforces a clear "
            "separation between the client and server code."
            ,
            id="instruction")

class AdvancedOptionsTips(HorizontalGroup):
    def compose(self) -> ComposeResult:
        yield Label("Advanced Options", id="advancedoptions")

class AdvancedOptions(HorizontalGroup):
    def compose(self) -> ComposeResult:
        yield AdvancedOptionsArgumentSelect()
        yield AdvancedOptionsInstruction()

class GenerateOptions(VerticalGroup):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Enter the generated file path.", id="fpinput")
        yield Button("Generate", id="generate")
        yield Label("Successfully Generated! Press Ctrl+Q to exit.", id="success")
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "generate":
            generate()
            self.add_class("success")
    def on_input_changed(self, event: Input.Changed) -> None:
        arguments["file_path"] = event.value

class TemplateModGeneratorApp(App):

    CSS_PATH = "generator.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        self.title = "Fabric Template Mod Generator"
        self.theme = "flexoki"
        yield Header()
        yield Footer()
        yield VerticalScroll(ModNameArgumentInput(),
                             ModIDArgumentInput(),
                             PackageNameArgumentInput(),
                             ModVersionArgumentInput(),
                             DescriptionArgumentInput(),
                             ProjectLicenseArgumentInput(),
                             LicenseFullNameArgumentInput(),
                             AuthorsArgumentInput(),
                             HomePageArgumentInput(),
                             ModSourceArgumentInput(),
                             AdvancedOptionsTips(),
                             AdvancedOptions(),
                             GenerateOptions(),
                             )

    def action_toggle_dark(self) -> None:
        self.theme = (
            "flexoki" if self.theme == "catppuccin-latte" else "catppuccin-latte"
        )

if __name__ == "__main__":
    app = TemplateModGeneratorApp(watch_css=True)
    app.run()