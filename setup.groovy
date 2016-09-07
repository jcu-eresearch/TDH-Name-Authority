(_p = new Properties()).load(new FileInputStream(new File("build.properties")))
project.properties.load(new FileInputStream(new File("build.properties")));

if(project.properties.containsKey("mint.project.home")){
    project.properties["project.home"] =  project.properties["mint.project.home"];
}
String projectHome = project.properties["project.home"];
if (projectHome == null) {
    String userHome = System.getProperty("user.home");
    File mintHome = new File(new File(userHome, "deployment"), "mint");
    project.properties["project.home"] = mintHome.absolutePath;

}
ph = new File(".project-home")
ph.write(project.properties["project.home"])

project.properties["app.location.linux"] =   project.properties["project.home"];
project.properties["app.location.windows"] = project.properties["project.home"];

println "Project will be deployed to: " + project.properties["project.home"];


java.net.InetAddress address = InetAddress.getByName(System.getenv("COMPUTERNAME"));
project.properties["ip.address"] = address.getHostAddress();
println "Computer IP Address: " + project.properties["ip.address"];

//Setup the hostname
if (project.properties.containsKey("local.mint.hostname")){
    project.properties["mint.hostname"] = project.properties["local.mint.hostname"]
    println "Hostname overridden to: " + project.properties["mint.hostname"]
}
project.properties["server.url.base"] = project.properties["mint.hostname"]+"/"+project.properties["mint.context"]+"/"