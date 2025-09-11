import shellsmith
import time
import random
from shellsmith.utils import base64_encoded

def float_to_dict(number):
    str_number = str(number)  # Convert to string
    return {i: char for i, char in enumerate(str_number)}

class SingleShell():
    def __init__(self, host, idShort, get_latest=True):

        self.host               = host
        self.idShort            = idShort
        self.repo               = shellsmith.get_shells(host)
        self.submodels          = shellsmith.get_submodels(host)
        self.shells_id          = self.get_shell_ids_with_idShort(idShort, self.repo)
        

        if get_latest:
            ts_list = []
            for i, shell_id in enumerate(self.shells_id):
                shell   = shellsmith.get_shell(shell_id, host=host)
                time.sleep(0.25)
                self.sm_dict = self.get_submodel_dict(shell)
                time.sleep(0.25)
                try:

                    ts_value = self.read_SME("ProductIdentification", "OrderTimestamp")["value"]
                    time.sleep(0.25)
                    if ts_value == "":
                        pass
                    else: ts_list.append([i,int(ts_value)])
                except Exception as e:
                    print(f"SM not found: {e}")
            
    
        # search for max#
        if ts_list:
            try:
                max_index, max_timestamp = max(enumerate(ts_list), key=lambda x: x[1][1])
                print(max_index)
                self.shell              = shellsmith.get_shell(self.shells_id[max_index], host=host)
                self.sm_dict            = self.get_submodel_dict()
                
            except:
                pass

        self.shell_id_base64    = base64_encoded(self.shell["id"], encode=True)
            

    def get_shell_ids_with_idShort(self, idShort, repo):
        self.shells_id = []
        for shell in repo:
            try:
                if idShort in shell["idShort"]:
                    self.shells_id.append(shell["id"])
            except:
                KeyError
            
        return self.shells_id

    def get_submodel_dict(self, shell=None):
        s_dict = {}
        if shell:
            self.shell = shell
        for i, sm in enumerate(self.shell["submodels"]):
            try:
                tmp = shellsmith.get_submodel(sm["keys"][0]["value"], host=self.host)
                s_dict[tmp["idShort"]]    = tmp["id"]
            except Exception as e:
                print(f"Error getting sm: {e}")
                pass
        return s_dict
    
    def read_SME(self, sm_idshort, element):
        return shellsmith.get_submodel_element(submodel_id=self.sm_dict[sm_idshort], id_short_path=element, host=self.host)

    def write_SME(self, sm_idshort, element, value):
        return shellsmith.patch_submodel_element_value(submodel_id=self.sm_dict[sm_idshort], id_short_path=element, value=value, host=self.host)
    
    def update_repo(self):
        self.repo               = shellsmith.get_shells(self.host)
        self.submodels          = shellsmith.get_submodels(self.host)
        self.shells_id          = self.get_shell_ids_with_idShort(self.idShort, self.repo)
        self.shell              = shellsmith.get_shell(self.shells_id[0], host=self.host)
        self.sm_dict            = self.get_submodel_dict()
        self.shell_id_base64    = base64_encoded(self.shell["id"], encode=True)

    def get_latest(self):
        self.update_repo()
        ts_list = []
        for i, shell_id in enumerate(self.shells_id):
            shell   = shellsmith.get_shell(shell_id, host=self.host)
            time.sleep(0.25)
            self.sm_dict = self.get_submodel_dict(shell)
            time.sleep(0.25)
            ts_value = self.read_SME("ProductIdentification", "OrderTimestamp")["value"]
            time.sleep(0.25)
            if ts_value == "":
                pass
            else: ts_list.append([i,int(ts_value)])
        
        # search for max#
        try:
            max_index, max_timestamp = max(enumerate(ts_list), key=lambda x: x[1][1])
            print(max_index)
            self.shell              = shellsmith.get_shell(self.shells_id[max_index], host=self.host)
            self.sm_dict            = self.get_submodel_dict()
            
        except:
            pass

    
if __name__ == "__main__":

    HOST_SRC            = "http://172.17.10.74:8000"
    #HOST_SRC            = "http://localhost:8000"
    HOST_TARGET         = "http://localhost:8081"

    target_shell = SingleShell(HOST_TARGET, "Semitrailer_Body_White", get_latest=True)
    print(target_shell.shell_id_base64)
    source_shell = SingleShell(HOST_SRC, "Semitrailer", get_latest=True)
    print(source_shell.shell_id_base64)
    
    
    while True: 

        try:
            # Value Mapping
            # OrderNumber
            s_order_nr = source_shell.read_SME("ProductIdentification", "OrderNumber")["value"]
            target_shell.write_SME("ProductIdentification", "OrderNumber", value=s_order_nr)
        
            # OrderTimestamp
            s_order_ts = source_shell.read_SME("ProductIdentification", "OrderTimestamp")["value"]
            if s_order_ts == '':
                s_order_ts = str(time.time())
            target_shell.write_SME("ProductIdentification", "OrderTimestamp", value=s_order_ts)

            # Manufacturing Process
            target_shell.write_SME("Processes", "ProcessType", value="Additive Manufacturing")

            # Quality Control
            qc = source_shell.read_SME("QualityInformation", "QualityStatus")["value"]
            target_shell.write_SME("QualityControl", "QCResult.Result", value="Tolerances exceeded")
            
            # Measures
            target_shell.write_SME("QualityControl", "QCResult.Remarks", value="Welding Needed")
            
            # Current PCF
            current_pcf = source_shell.read_SME("CarbonFootprint", "ProductCarbonFootprint.PCFReferenceValueForCalculation")
            if not current_pcf:
                random_value = str(round(random.uniform(1.62, 1.82), 2))
            target_shell.write_SME("CarbonFootprint", "ProductCarbonFootprint.PCFReferenceValueForCalculation", value=random_value)
            
            # Energy Cons
            random_value = str(round(random.uniform(0.3, 0.6), 2))
            target_shell.write_SME("EnergyData", "Consumption.EnergyAmountValue.TotalEnergyConsumption", value=random_value)
            
            # New PCF
            if current_pcf:
                rd = round(random.uniform(1, 2))
                new_value = int(current_pcf)+rd
                target_shell.write_SME("CarbonFootprint", "ProductCarbonFootprint.PCFCO2eq", value=new_value)
            else: random_value = str(round(random.uniform(1.9, 2.1), 2))
            target_shell.write_SME("CarbonFootprint", "ProductCarbonFootprint.PCFCO2eq", value=random_value)

            time.sleep(5)
        except Exception as e:
            print(f"Error: {e}")
