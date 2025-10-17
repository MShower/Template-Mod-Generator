import os
import shutil
import json
import time


class Generator:

    def __init__(self, authors: list, contact: dict, description: str, project_license: str, license_full_name: str,
                 mod_name: str, mod_id: str, mod_version: str,
                 package_name: str, kotlin: bool, mojang_mappings: bool, datagen: bool,
                 split_client_and_common_sources: bool, remove_license: bool):
        self.mod_version = mod_version
        self.license_full_name = license_full_name
        self.contact = contact
        self.authors = authors
        self.description = description
        self.license = project_license
        self.mod_name = mod_name
        self.mod_id = mod_id
        self.main_name = mod_name.replace(" ", "")
        self.folder_name = self.mod_name
        self.package_name = package_name
        self.kotlin = kotlin
        self.mojang_mappings = mojang_mappings
        self.datagen = datagen
        self.split_client_and_common_sources = split_client_and_common_sources
        self.remove_license = remove_license

    def parse_package_name(self):
        return self.package_name.split('.')

    def get_src_absolute_path(self):
        return os.path.abspath(".")

    def rename_main_folder(self, old_folder_name):
        os.rename(old_folder_name, self.folder_name)

    def chdir(self):
        os.chdir(self.folder_name)

    def remove_file(self):
        if self.remove_license:
            os.remove("LICENSE")
        os.remove("HEADER.txt")
        os.remove("jitpack.yml")
        os.remove("build.gradle")
        os.remove("README.md")
        os.remove("gradle.properties")
        os.remove("settings.gradle")
        os.remove("common.gradle")

    def rebuild_package(self, mod_abspath:str, parsed_package: list):
        os.chdir("src" + os.path.sep + "main")
        try:
            shutil.rmtree("java")
        except FileNotFoundError:
            pass
        os.mkdir("java")
        os.chdir("java")
        for folder_name in parsed_package:
            os.mkdir(folder_name)
            os.chdir(folder_name)
        os.mkdir("mixins")
        os.chdir("mixins")
        with open("ExampleMixin.java", "w") as f:
            f.write(
                "package {}.mixin;\n".format(self.package_name) +
                "\n"
                "import net.minecraft.server.MinecraftServer;\n"
                "import org.spongepowered.asm.mixin.Mixin;\n"
                "import org.spongepowered.asm.mixin.injection.At;\n"
                "import org.spongepowered.asm.mixin.injection.Inject;\n"
                "import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;\n"
                "\n"
                "@Mixin(MinecraftServer.class)\n"
                "public class ExampleMixin {\n"
                "	@Inject(at = @At(\"HEAD\"), method = \"loadWorld\")\n"
                "	private void init(CallbackInfo info) {\n"
                "		// This code is injected into the start of MinecraftServer.loadWorld()V\n"
                "	}\n"
                "}")
            f.close()
        os.chdir("..")
        with open(self.main_name + ".java", "w") as f:
            f.write(
                "package {};\n".format(self.package_name) +
                "\n"
                "import net.fabricmc.api.ModInitializer;\n"
                "import net.fabricmc.loader.api.FabricLoader;\n"
                "import net.fabricmc.loader.api.metadata.ModMetadata;\n"
                "\n"
                "//#if MC >= 11802\n"
                "//$$ import com.mojang.logging.LogUtils;\n"
                "//$$ import org.slf4j.Logger;\n"
                "//#else\n"
                "import org.apache.logging.log4j.LogManager;\n"
                "import org.apache.logging.log4j.Logger;\n"
                "//#endif\n"
                "\n"
                "public class {} implements ModInitializer\n".format(self.main_name) +
                "{\n"
                "	public static final Logger LOGGER =\n"
                "			//#if MC >= 11802\n"
                "			//$$ LogUtils.getLogger();\n"
                "			//#else\n"
                "			LogManager.getLogger();\n"
                "			//#endif\n"
                "\n"
                f"	public static final String MOD_ID = \"{self.mod_id}\";\n" +
                "	public static String MOD_VERSION = \"{}\";\n".format(self.mod_version) +
                "	public static String MOD_NAME = \"{}\";\n".format(self.mod_name) +
                "\n"
                "	@Override\n"
                "	public void onInitialize()\n"
                "	{\n"
                "ModMetadata metadata = FabricLoader.getInstance().getModContainer(MOD_ID).orElseThrow("
                "RuntimeException::new).getMetadata();\n"
                "		MOD_NAME = metadata.getName();\n"
                "		MOD_VERSION = metadata.getVersion().getFriendlyString();\n"
                "	}\n"
                "}\n"
            )
            f.close()
        os.chdir(mod_abspath + os.path.sep + "src" + os.path.sep + "main" + os.path.sep + "resources")
        print(os.path.abspath("."))
        with open("fabric.mod.json", "r") as f:
            fabric_mod_json_cfg = json.load(f)
            fabric_mod_json_cfg["description"] = self.description
            fabric_mod_json_cfg["authors"] = self.authors
            fabric_mod_json_cfg["license"] = self.license
            fabric_mod_json_cfg["contact"] = self.contact
            fabric_mod_json_cfg["icon"] = "assets/" + self.mod_id + "/icon.png"
            fabric_mod_json_cfg["entrypoints"]["main"][0] = self.package_name + "." + self.main_name
            fabric_mod_json_cfg["mixins"][0] = self.mod_id + ".mixins.json"
            f.close()
        with open("fabric.mod.json", "w+") as f:
            json.dump(fabric_mod_json_cfg, f, indent=4)
            f.close()
        with open("template_mod.mixins.json", "r") as f:
            mixin_cfg = json.load(f)
            mixin_cfg["package"] = self.package_name + ".mixins"
            mixin_cfg["mixins"][0] = "ExampleMixin"
            f.close()
        with open("template_mod.mixins.json", "w+") as f:
            json.dump(mixin_cfg, f, indent=4)
            f.close()
        os.rename("template_mod.mixins.json", self.mod_id + ".mixins.json")
        os.chdir("assets")
        os.rename("template_mod", self.mod_id)
        os.chdir(mod_abspath)
        with open("build.gradle", "w+") as f:
            f.write("plugins {\n"
                    "	id 'maven-publish'\n"
                    "	id 'fabric-loom' version '1.11-SNAPSHOT' apply false\n"
                    "\n"
                    "	// https://github.com/ReplayMod/preprocessor\n"
                    "	// https://github.com/Fallen-Breath/preprocessor\n"
                    "	id 'com.replaymod.preprocess' version 'd452ef7612'\n"
                    "}\n"
                    "\n"
                    "preprocess {\n"
                    "	strictExtraMappings = false\n"
                    "\n"
                    "	def mc114  = createNode('1.14.4', 1_14_04, '')\n"
                    "	def mc115  = createNode('1.15.2', 1_15_02, '')\n"
                    "	def mc116  = createNode('1.16.5', 1_16_05, '')\n"
                    "	def mc117  = createNode('1.17.1', 1_17_01, '')\n"
                    "	def mc118  = createNode('1.18.2', 1_18_02, '')\n"
                    "	def mc119  = createNode('1.19.4', 1_19_04, '')\n"
                    "	def mc1204 = createNode('1.20.4', 1_20_04, '')\n"
                    "	def mc1206 = createNode('1.20.6', 1_20_06, '')\n"
                    "	def mc1211 = createNode('1.21.1', 1_21_01, '')\n"
                    "	def mc1213 = createNode('1.21.3', 1_21_03, '')\n"
                    "	def mc1214 = createNode('1.21.4', 1_21_04, '')\n"
                    "	def mc1215 = createNode('1.21.5', 1_21_05, '')\n"
                    "	def mc1218 = createNode('1.21.8', 1_21_08, '')\n"
                    "	def mc12110 = createNode('1.21.10', 1_21_10, '')\n"
                    "\n"
                    "	mc115 .link(mc114 , null)\n"
                    "	mc115 .link(mc116 , null)\n"
                    "	mc116 .link(mc117 , null)\n"
                    "	mc117 .link(mc118 , null)\n"
                    "	mc118 .link(mc119 , null)\n"
                    "	mc119 .link(mc1204, null)\n"
                    "	mc1204.link(mc1206, null)\n"
                    "	mc1206.link(mc1211, null)\n"
                    "	mc1211.link(mc1213, null)\n"
                    "	mc1213.link(mc1214, null)\n"
                    "	mc1214.link(mc1215, null)\n"
                    "	mc1215.link(mc1218, null)\n"
                    "	mc1218.link(mc12110, null)\n"
                    "}\n"
                    "\n"
                    "tasks.register('buildAndGather') {\n"
                    "	subprojects {\n"
                    "		dependsOn project.tasks.named('build').get()\n"
                    "	}\n"
                    "	doFirst {\n"
                    "		println 'Gathering builds'\n"
                    "		def buildLibs = {\n"
                    "			p -> p.buildDir.toPath().resolve('libs')\n"
                    "		}\n"
                    "		delete fileTree(buildLibs(rootProject)) {\n"
                    "			include '*'\n"
                    "		}\n"
                    "		subprojects {\n"
                    "			copy {\n"
                    "				from(buildLibs(project)) {\n"
                    "					include '*.jar'\n"
                    "					exclude '*-dev.jar', '*-sources.jar', '*-shadow.jar'\n"
                    "				}\n"
                    "				into buildLibs(rootProject)\n"
                    "				duplicatesStrategy = DuplicatesStrategy.INCLUDE\n"
                    "			}\n"
                    "		}\n"
                    "	}\n"
                    "}\n")
            f.close()
        with open("common.gradle", "w+") as f:
            f.write("apply plugin: 'maven-publish'\n"
                    "apply plugin: 'fabric-loom'\n"
                    "apply plugin: 'com.replaymod.preprocess'\n"
                    "\n"
                    "int mcVersion = project.mcVersion\n"
                    "\n"
                    "repositories {\n"
                    "}\n"
                    "\n"
                    "// https://github.com/FabricMC/fabric-loader/issues/783\n"
                    "configurations {\n"
                    "	modRuntimeOnly.exclude group: 'net.fabricmc', module: 'fabric-loader'\n"
                    "}\n"
                    "\n"
                    "dependencies {\n"
                    "	// loom\n"
                    "	minecraft \"com.mojang:minecraft:${project.minecraft_version}\"\n"
                    "	mappings \"net.fabricmc:yarn:${project.yarn_mappings}:v2\"\n"
                    "	modImplementation \"net.fabricmc:fabric-loader:${project.loader_version}\"\n"
                    "}\n"
                    "\n" +
                    "String MIXIN_CONFIG_PATH = '{}.json'\n".format(self.mod_id + ".mixins.json") +
                    "String LANG_DIR = 'assets/{}/lang'\n".format(self.mod_id) +
                    "JavaVersion JAVA_COMPATIBILITY\n"
                    "if (mcVersion >= 12005) {\n"
                    "	JAVA_COMPATIBILITY = JavaVersion.VERSION_21\n"
                    "} else if (mcVersion >= 11800) {\n"
                    "	JAVA_COMPATIBILITY = JavaVersion.VERSION_17\n"
                    "} else if (mcVersion >= 11700) {\n"
                    "	JAVA_COMPATIBILITY = JavaVersion.VERSION_16\n"
                    "} else {\n"
                    "	JAVA_COMPATIBILITY = JavaVersion.VERSION_1_8\n"
                    "}\n"
                    "JavaVersion MIXIN_COMPATIBILITY_LEVEL = JAVA_COMPATIBILITY\n"
                    "\n"
                    "loom {\n"
                    "	def commonVmArgs = ['-Dmixin.debug.export=true', '-Dmixin.debug.countInjections=true']\n"
                    "	runConfigs.configureEach {\n"
                    "		// to make sure it generates all \"Minecraft Client (:subproject_name)\" applications\n"
                    "		ideConfigGenerated = true\n"
                    "		runDir '../../run'\n"
                    "		vmArgs commonVmArgs\n"
                    "	}\n"
                    "}\n"
                    "\n"
                    "String modVersionSuffix = ''\n"
                    "String artifactVersion = project.mod_version\n"
                    "String artifactVersionSuffix = ''\n"
                    "// detect github action environment variables\n"
                    "// https://docs.github.com/en/actions/learn-github-actions/environment-variables#default-environment-variables\n"
                    "if (System.getenv(\"BUILD_RELEASE\") != \"true\") {\n"
                    "	String buildNumber = System.getenv(\"BUILD_ID\")\n"
                    "	modVersionSuffix += buildNumber != null ? ('+build.' + buildNumber) : '-SNAPSHOT'\n"
                    "	artifactVersionSuffix = '-SNAPSHOT'  // A non-release artifact is always a SNAPSHOT artifact\n"
                    "}\n"
                    "String fullModVersion = project.mod_version + modVersionSuffix\n"
                    "String fullProjectVersion, fullArtifactVersion\n"
                    "\n"
                    "// Example version values:\n"
                    "//   project.mod_version     1.0.3                      (the base mod version)\n"
                    "//   modVersionSuffix        +build.88                  (use github action build number if possible)\n"
                    "//   artifactVersionSuffix   -SNAPSHOT\n"
                    "//   fullModVersion          1.0.3+build.88             (the actual mod version to use in the mod)\n"
                    "//   fullProjectVersion      v1.0.3-mc1.15.2+build.88   (in build output jar name)\n"
                    "//   fullArtifactVersion     1.0.3-mc1.15.2-SNAPSHOT    (maven artifact version)\n"
                    "\n"
                    "group = project.maven_group\n"
                    "base.archivesName = project.archives_base_name\n"
                    "fullProjectVersion = 'v' + project.mod_version + '-mc' + project.minecraft_version + modVersionSuffix\n"
                    "fullArtifactVersion = artifactVersion + '-mc' + project.minecraft_version + artifactVersionSuffix\n"
                    "version = fullProjectVersion\n"
                    "\n"
                    "// See https://youtrack.jetbrains.com/issue/IDEA-296490\n"
                    "// if IDEA complains about \"Cannot resolve resource filtering of MatchingCopyAction\" and you want to know why\n"
                    "processResources {\n"
                    "	inputs.property \"id\", project.mod_id\n"
                    "	inputs.property \"name\", project.mod_name\n"
                    "	inputs.property \"version\", fullModVersion\n"
                    "	inputs.property \"minecraft_dependency\", project.minecraft_dependency\n"
                    "\n"
                    "	filesMatching(\"fabric.mod.json\") {\n"
                    "		def valueMap = [\n"
                    "				\"id\": project.mod_id,\n"
                    "				\"name\": project.mod_name,\n"
                    "				\"version\": fullModVersion,\n"
                    "				\"minecraft_dependency\": project.minecraft_dependency,\n"
                    "		]\n"
                    "		expand valueMap\n"
                    "	}\n"
                    "\n"
                    "	filesMatching(MIXIN_CONFIG_PATH) {\n"
                    "		filter { s -> s.replace('{{COMPATIBILITY_LEVEL}}', \"JAVA_${MIXIN_COMPATIBILITY_LEVEL.ordinal() + 1}\") }\n"
                    "	}\n"
                    "}\n"
                    "\n"
                    "\n"
                    "// ensure that the encoding is set to UTF-8, no matter what the system default is\n"
                    "// this fixes some edge cases with special characters not displaying correctly\n"
                    "// see http://yodaconditions.net/blog/fix-for-java-file-encoding-problems-with-gradle.html\n"
                    "tasks.withType(JavaCompile).configureEach {\n"
                    "	options.encoding = \"UTF-8\"\n"
                    "	options.compilerArgs << \"-Xlint:deprecation\" << \"-Xlint:unchecked\"\n"
                    "	if (JAVA_COMPATIBILITY <= JavaVersion.VERSION_1_8) {\n"
                    "		// suppressed \"source/target value 8 is obsolete and will be removed in a future release\"\n"
                    "		options.compilerArgs << '-Xlint:-options'\n"
                    "	}\n"
                    "}\n"
                    "\n"
                    "java {\n"
                    "	sourceCompatibility = JAVA_COMPATIBILITY\n"
                    "	targetCompatibility = JAVA_COMPATIBILITY\n"
                    "\n"
                    "	// Loom will automatically attach sourcesJar to a RemapSourcesJar task and to the \"build\" task\n"
                    "	// if it is present.\n"
                    "	// If you remove this line, sources will not be generated.\n"
                    "	withSourcesJar()\n"
                    "}\n"
                    "\n"
                    "jar {\n"
                    "	from(rootProject.file('LICENSE')) {\n"
                    "		rename { \"${it}\" }\n"
                    "	}\n"
                    "    from(rootProject.file('NOTICE')) {\n"
                    "        rename { \"${it}\" }\n"
                    "    }\n"
                    "}\n"
                    "\n"
                    "// configure the maven publication\n"
                    "publishing {\n"
                    "	publications {\n"
                    "		mavenJava(MavenPublication) {\n"
                    "			from components.java\n"
                    "			artifactId = base.archivesName.get()\n"
                    "			version = fullArtifactVersion\n"
                    "		}\n"
                    "	}\n"
                    "\n"
                    "	// select the repositories you want to publish to\n"
                    "	repositories {\n"
                    "	}\n"
                    "}\n")
            f.close()
        with open("gradle.properties", "w+") as f:
            f.write(
                "# Gradle Properties\n"
                "	org.gradle.jvmargs=-Xmx6G\n"
                "\n"
                "# Fabric Basic Properties\n"
                "	# https://fabricmc.net/versions.html\n"
                "	loader_version=0.17.3\n"
                "\n"
                "# Mod Properties\n" +
                "	mod_id={}\n".format(self.mod_id) +
                "	mod_name={}\n".format(self.mod_name) +
                "	mod_version={}\n".format(self.mod_version) +
                "	maven_group={}\n".format(self.package_name) +
                "	archives_base_name={}\n".format(self.mod_id) +
                "\n"
                "\n"
                "# Global Dependencies"
            )
            f.close()
        with open("NOTICE", "w+") as f:
            author = ""
            for name in self.authors:
                author = author + name + " "
            f.write("This project includes code from:\n"
                    "\n"
                    "TemplateMod\n"
                    "  Copyright (C) 2023 Fallen_Breath\n"
                    "  Licensed under the GNU Lesser General Public License v3.0\n"
                    "  <https://github.com/Fallen-Breath/fabric-mod-template>\n"
                    "\n"
                    "------------------------------------------------------\n"
                    "\n"
                    "Except for the portions noted above,\n"
                    "all other source code in this repository is\n" +
                    "Copyright (C) {} {}\n".format(time.strftime("%Y", time.localtime()), author) +
                    "and is released under the {}.".format(self.license_full_name))
            f.close()
        with open("settings.gradle", "w+") as f:
            f.write("import groovy.json.JsonSlurper\n"
                    "\n"
                    "pluginManagement {\n"
                    "	repositories {\n"
                    "		maven {\n"
                    "			name = 'Fabric'\n"
                    "			url = 'https://maven.fabricmc.net/'\n"
                    "		}\n"
                    "		maven {\n"
                    "			name = 'Jitpack'\n"
                    "			url = 'https://jitpack.io'\n"
                    "		}\n"
                    "		mavenCentral()\n"
                    "		gradlePluginPortal()\n"
                    "	}\n"
                    "	resolutionStrategy {\n"
                    "		eachPlugin {\n"
                    "			switch (requested.id.id) {\n"
                    "				case \"com.replaymod.preprocess\": {\n"
                    "					useModule(\"com.github.Fallen-Breath:preprocessor:${requested.version}\")\n"
                    "					break\n"
                    "				}\n"
                    "			}\n"
                    "		}\n"
                    "	}\n"
                    "}\n"
                    "\n"
                    "def settings = new JsonSlurper().parseText(file('settings.json').text)\n"
                    "for (String version : settings.versions) {\n"
                    "	include(\":$version\")\n"
                    "\n"
                    "	def proj = project(\":$version\")\n"
                    "	proj.projectDir = file(\"versions/$version\")\n"
                    "	proj.buildFileName = \"../../common.gradle\"\n"
                    "}\n")
            f.close()
