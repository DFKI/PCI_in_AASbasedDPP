from nicegui import app, ui
from aas_parser.synchronizer import SingleShell
from datetime import datetime, timedelta
import random
import locale
import uuid

# API Endpoint (replace with actual API)
HOST = "http://localhost:8081"
SOURCE_SHELL_IDSHORT = "Semitrailer_Body_White"
#locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")

# Set data source shell
sources_shell = SingleShell(HOST, SOURCE_SHELL_IDSHORT, get_latest=True)

# UI Elements for Dynamic Data
data_labels = {"real": {}, "simulated": {}}
simulated_data_cache = {}  # Ensure it's initialized

def fetch_real_data():
    """Fetch data from API."""
    try:
        sources_shell.get_latest()
        read_error = False
    except:
        read_error = True 
        print({"error": "Error when retrieving the real data!"}) 
        return read_error

def fetch_simulated_data():
    """Generate random simulated data."""
    product_name = ["Semitrailer", "Semitrailer_Chassis", "Semitrailer_Truck", "Truck"]
    random_timestamp = int((datetime.now() + timedelta(days=random.randint(-30, 30))).timestamp())
    random_time = datetime.fromtimestamp(random_timestamp).strftime("%B %d, %Y at %I:%M:%S %p UTC")
    return {
        "Product_Name": f"Produkt {random.choice(product_name)}",
        "Product_Order_Number": str(uuid.uuid4()),
        "Production_Date": random_time,
        "Manufacturing_Process": random.choice(["Additive Manufacturing", "Milling", "Welding"]),
        "Quality_Control": random.choice(["Tolerance Exceeded", "Within Tolerances"]),
        "Measures": random.choice(["Soldering", "Discarding", "Rework"]),
        "Current_PCF_Value_[kg]": round(random.uniform(1.5, 2.5), 2),
        "Energy_Consumption_[kWh]": f"{round(random.uniform(0.2, 0.5), 2)} kWh",
        "New_PCF_Value_[kg]": round(random.uniform(2.0, 3.5), 2),
    }

# Initialize `simulated_data_cache` with valid keys
simulated_data_cache = fetch_simulated_data()

def update_data():
    """Fetch new data (real & simulated) and update the UI."""
    global simulated_data_cache

    if not simulation_mode.value:
        simulated_data = simulated_data_cache  # Keep simulation data static when real data is active
        read_error = fetch_real_data()

    else:
        real_data = {key: "In Simulation Mode" for key in simulated_data_cache}  # Use valid keys
        simulated_data = fetch_simulated_data()
        simulated_data_cache = simulated_data  # Store latest simulation data
        read_error = False

    real_opacity = "0.3" if simulation_mode.value else "1.0"
    simulated_opacity = "1.0" if simulation_mode.value else "0.3"

    for key in data_labels["real"]:
        if read_error:
            data_labels["real"][key].set_text(f"⚠️ {real_data['error']}")
        
        elif key == 'Product_Name': 
            pr_name = sources_shell.shell["idShort"]
            data_labels["real"][key].set_text(f"{pr_name}")

        elif "Product_Order_Number" in key:
            order_number    = sources_shell.read_SME("ProductIdentification", "OrderNumber")["value"]
            data_labels["real"][key].set_text(f"{order_number}")

        elif "Production_Date" in key:
            # Format in a readable way
            pr_date = sources_shell.read_SME("ProductIdentification", "OrderTimestamp")["value"]
            if pr_date == "":
                pass
            else: 
                pr_date         = int(sources_shell.read_SME("ProductIdentification", "OrderTimestamp")["value"])/1000
                readable_time   = datetime.fromtimestamp(pr_date).strftime("%B %d, %Y at %I:%M:%S %p UTC")
                data_labels["real"][key].set_text(f"{readable_time}")

        elif "Manufacturing_Process" in key:
            man_proc        = sources_shell.read_SME("Processes", "ProcessType")["value"]
            data_labels["real"][key].set_text(f"{man_proc}")

        elif "Quality_Control" in key:
            try:
                qc              = sources_shell.read_SME("QualityControl", "QCResult.Result")["value"]
            except:
                qc = "KeyError"
            data_labels["real"][key].set_text(f"{qc}")

        elif "Measures" in key:
            try:
                mea             = sources_shell.read_SME("QualityControl", "QCResult.Remarks")["value"]
            except:
                mea = "KeyError"
                
            data_labels["real"][key].set_text(f"{mea}")

        elif "Current_PCF_Value" in key:
            c_pcf           = sources_shell.read_SME("CarbonFootprint", "ProductCarbonFootprint.PCFReferenceValueForCalculation")["value"]
            data_labels["real"][key].set_text(f"{c_pcf}")

        elif "Energy_Consumption" in key:
            en_cons         = sources_shell.read_SME("EnergyData", "Consumption.EnergyAmountValue.TotalEnergyConsumption")["value"]
            data_labels["real"][key].set_text(f"{en_cons}")

        elif "New_PCF_Value" in key:
            n_pcf           = sources_shell.read_SME("CarbonFootprint", "ProductCarbonFootprint.PCFCO2eq")["value"]
            data_labels["real"][key].set_text(f"{n_pcf}")

        data_labels["real"][key].style(f"opacity: {real_opacity}; font-size: 1.5em; font-weight: bold; padding: 10px; border: 2px solid black; background: white;")

    for key in data_labels["simulated"]:
        data_labels["simulated"][key].set_text(f"{simulated_data.get(key, 'N/A')}")
        data_labels["simulated"][key].style(f"opacity: {simulated_opacity}; font-size: 1.5em; font-weight: bold; padding: 10px; border: 2px solid black; background: white;")

# ----------------------------------------------------------------
# Header Section with Logos and Links
# ----------------------------------------------------------------
with ui.row().style("justify-content: space-between; width: 100%; padding: 5px;"):
    ui.image("assets/logos/dace.png").style("width: 250px; height: auto; position: absolute; top: 10px; left: 10px;")
    ui.image("assets/logos/dfki.png").style("width: 250px; height: auto; position: absolute; top: 10px; left: 500px;")
    ui.image("assets/logos/sf_logo.png").style("width: 300px; height: auto; position: absolute; middle: 10px; left: 925px; margin-top: 10px")
    ui.image("assets/logos/dace.png").style("width: 180px; height: auto; position: absolute; top: 10px; left: 1500px;")
    with ui.column().style("align-items: flex-end;"):
        simulation_mode = ui.switch("Simulation-mode (Test-data)").style("font-size: 20px; position: absolute; top: 20px; right: 20px;")
        simulation_mode.on(lambda: update_data())
        
with ui.row().style("justify-content: space-around; align-items: center; width: 100%; margin-top: 10px;"):
        ui.link("Visit DACE", "https://dace-info.de/").props('target="_blank"').style("font-size: 20px; position: absolute; top: 120px; left: 80px;")
        ui.link("Visit DFKI", "https://www.dfki.de/web/ueber-uns/standorte-kontakt/kaiserslautern-trier").props('target="_blank"').style("font-size: 20px; position: absolute; top: 120px; left: 550px;")
        ui.link("Visit Smartfactory", "https://www.smartfactory.de/").props('target="_blank"').style("font-size: 20px; position: absolute; top: 120px; left: 1000px;")
        
ui.separator().style("margin-top: 100px;")  # Adds spacing below the logo

ui.label("Comparison of production data").style("font-size: 30px; font-weight: bold; text-align: center; margin-bottom: 5px;")

with ui.row().style("display: flex; justify-content: space-between; align-items: center; width: 100%;"):
    
    with ui.row().style("display: flex; gap: 30px;"):
        # Fixed Label Column with gradient and border, fixed width
        with ui.column().style("width: 300px;"):
            ui.label("Data field").style("font-weight: bold; text-decoration: underline; font-size: 2em; padding: 2px")

            field_colors = {
                "Product_Name": "#85C1E9",  # Light Blue
                "Product_Order_Number": "#85C1E9",
                "Production_Date": "#85C1E9",
                "Manufacturing_Process": "#D7BDE2",  # Light Purple
                "Quality_Control": "#D7BDE2",
                "Measures": "#D7BDE2",
                "Current_PCF_Value_[kg]": "#A9DFBF",  # Green
                "Energy_Consumption_[kWh]": "#A9DFBF",
                "New_PCF_Value_[kg]": "#A9DFBF"
            }

            for key in simulated_data_cache:
                ui.label(key.replace("_", " ")).style(f"font-size: 1.5em; font-weight: bold; padding: 10px; border: 2px solid black; background: {field_colors[key]}; width: 100%;")
        
        # Real Data Column
        with ui.column():
            ui.label("Data from the DPP*").style("font-weight: bold; color: blue; font-size: 2em;padding: 2px")
            for key in simulated_data_cache:
                data_labels["real"][key] = ui.label("...").style("opacity: 1.0; font-size: 1.5em; font-weight: bold; padding: 10px; border: 2px solid black; background: white; width: 100%;")
        
        # Simulated Data Column
        with ui.column():
            ui.label("Simulated data").style("font-weight: bold; color: red; font-size: 2em;padding: 2px")
            for key in simulated_data_cache:
                data_labels["simulated"][key] = ui.label("...").style("opacity: 0.3; font-size: 1.5em; font-weight: bold; padding: 10px; border: 2px solid black; background: white; width: 100%;")
    
    # ----------------------------------------------------------------
    # Video box and QR-codes
    # ----------------------------------------------------------------
    with ui.column().style("border: 2px solid black; padding: 10px; width: 1100px; display: flex; flex-direction: column; align-items: center;"):
        ui.label("This is DACE!").style("font-weight: bold; text-decoration: underline; font-size: 2em; text-align: center;")
        v=ui.video("assets/DACE_short.mp4", autoplay=True, loop=True, muted=True)

        # 🎯 QR Codes aligned under the video
        with ui.row().style("justify-content: center; gap: 50px; margin-top: 20px;"):
            for qr_path, label_text, icon in [
                ("assets/qrcodes/DACE_Homepage.png", "DACE Homepage", "🌐"),
                ("assets/qrcodes/DACE_Academy.png", "DACE Academy", "🎓"),
            ]:
                with ui.column().style("align-items: center;"):
                    ui.image(qr_path).style("width: 150px; height: 150px;")
                    ui.label(f"{icon} {label_text}").style("font-weight: bold; font-size: 1.2em; text-align: center;")

# ----------------------------------------------------------------
# Full-width footer container
# ----------------------------------------------------------------
with ui.row().style("width: 100%; background-color: #f0f0f0; padding: 30px; border-top: 2px solid #ccc; box-sizing: border-box;"):

    # Inner row to space content
    with ui.row().style("width: 100%; justify-content: space-between;"):

        # 📦 Left Box – Glossary
        with ui.column().style("background-color: white; border: 2px solid #aaa; border-radius: 12px; padding: 16px; width: 20%; box-shadow: 2px 2px 5px #ccc;"):
            ui.label("ℹ️  Glossary").style("font-weight: bold; font-size: 22px; text-decoration: underline; color: #000;")
            ui.label("DPP → Digital Product Passport").style("font-size: 18px; color: #333;")
            ui.label("PCF → Product Carbon Footprint").style("font-size: 18px; color: #333;")

        # 📦 Right Box – Hyperlink Buttons (centered inside the box)
        with ui.column().style("background-color: white; border: 2px solid #aaa; border-radius: 12px; padding: 20px; width: 36%; box-shadow: 2px 2px 5px #ccc; align-items: center;"):

            with ui.row().style("gap: 20px; justify-content: center; width: 100%;"):
                with ui.link("", target="http://172.17.10.74:5170/#/shell/aHR0cHM6Ly9zbWFydGZhY3RvcnkuZGUvc2hlbGxzLzBBVlFTMEV5bjE").props('target="_blank"'):
                    ui.label("SmartFactory ShellScape").style("padding: 20px 40px; background-color: #e3f2fd; border: 2px solid #2196f3; border-radius: 10px; font-weight: bold; font-size: 2em; color: #0d47a1; cursor: pointer;")

                with ui.link("", target="https://sfkl.mnestix.xitaso.net/en/viewer/aHR0cHM6Ly9zbWFydGZhY3RvcnkuZGUvc2hlbGxzLzBBVlFTMEV5bjE").props('target="_blank"'):
                    ui.label("Xitaso MNESTIX").style("padding: 20px 40px; background-color: #ffe0b2; border: 2px solid #fb8c00; border-radius: 10px; font-weight: bold; font-size: 2em; color: #e65100; cursor: pointer;")


app.on_startup(fetch_real_data)
# Initial Data Load
fetch_real_data()
update_data()

# Set up automatic data refresh every 5 seconds
ui.timer(1.0, update_data)

ui.run(port=8888,
       title="DPP meets AAS",
       dark=False,
       #window_size=(1920, 1080),
       #fullscreen=False
       )
