#!/usr/bin/env python3
# -*- coding: utf_8 -*-

from mypylib.mypylib import *
from mypyconsole.mypyconsole import *
from mytoncore import *

local = MyPyClass(__file__)
console = MyPyConsole()
ton = MyTonCore()

def Init():
	# Load translate table
	local.InitTranslator(local.buffer.get("myDir") + "translate.json")

	# Create user console
	console.name = "MyTonCtrl"
	console.startFunction = CheckMytonctrlUpdate

	console.AddItem("update", Update, local.Translate("update_cmd"))
	console.AddItem("upgrade", Upgrade, local.Translate("upgrade_cmd"))
	console.AddItem("installer", Installer, local.Translate("installer_cmd"))
	console.AddItem("status", PrintStatus, local.Translate("status_cmd"))
	console.AddItem("seqno", Seqno, local.Translate("seqno_cmd"))
	console.AddItem("getconfig", GetConfig, local.Translate("getconfig_cmd"))

	console.AddItem("nw", CreatNewWallet, local.Translate("nw_cmd"))
	console.AddItem("aw", ActivateWallet, local.Translate("aw_cmd"))
	console.AddItem("wl", PrintWalletsList, local.Translate("wl_cmd"))
	console.AddItem("iw", ImportWalletFromFile, local.Translate("iw_cmd"))
	console.AddItem("swa", SaveWalletAddressToFile, local.Translate("swa_cmd"))
	console.AddItem("dw", DeleteWallet, local.Translate("dw_cmd"))

	console.AddItem("vas", ViewAccountStatus, local.Translate("vas_cmd"))
	console.AddItem("vah", ViewAccountHistory, local.Translate("vah_cmd"))
	console.AddItem("mg", MoveGrams, local.Translate("mg_cmd"))

	console.AddItem("nb", CreatNewBookmark, local.Translate("nb_cmd"))
	console.AddItem("bl", PrintBookmarksList, local.Translate("bl_cmd"))
	console.AddItem("db", DeleteBookmark, local.Translate("db_cmd"))

	# console.AddItem("nr", CreatNewRule, local.Translate("nr_cmd")) # "Добавить правило в расписание / Create new rule"
	# console.AddItem("rl", PrintRulesList, local.Translate("rl_cmd")) # "Показать правила расписания / Show rule list"
	# console.AddItem("dr", DeleteRule, local.Translate("dr_cmd")) # "Удалить правило из расписания / Delete rule"

	console.AddItem("nd", NewDomain, local.Translate("nd_cmd"))
	console.AddItem("dl", PrintDomainsList, local.Translate("dl_cmd"))
	console.AddItem("vds", ViewDomainStatus, local.Translate("vds_cmd"))
	console.AddItem("dd", DeleteDomain, local.Translate("dd_cmd"))

	console.AddItem("ol", PrintOffersList, local.Translate("ol_cmd"))
	console.AddItem("vo", VoteOffer, local.Translate("vo_cmd"))
	console.AddItem("od", OfferDiff, local.Translate("od_cmd"))

	console.AddItem("el", PrintElectionEntriesList, local.Translate("el_cmd"))
	console.AddItem("ve", VoteElectionEntry, local.Translate("ve_cmd"))
	console.AddItem("vl", PrintValidatorList, local.Translate("vl_cmd"))
	console.AddItem("cl", PrintComplaintsList, local.Translate("cl_cmd"))
	console.AddItem("vc", VoteComplaint, local.Translate("vc_cmd"))


	console.AddItem("get", GetSettings, local.Translate("get_cmd"))
	console.AddItem("set", SetSettings, local.Translate("set_cmd"))

	console.AddItem("test", Test, "Test")
	console.AddItem("test2", Test2, "Test")
	console.AddItem("test3", Test3, "Test")
	console.AddItem("pt", PrintTest, "PrintTest")

	local.db["config"]["logLevel"] = "debug"
	local.db["config"]["isLocaldbSaving"] = True
	local.Run()
#end define

def Installer(args):
	args = ["python3", "/usr/src/mytonctrl/mytoninstaller.py"]
	subprocess.run(args)
#end define

def Update(args):
	exitCode = RunAsRoot(["bash", "/usr/src/mytonctrl/scripts/update.sh"])
	if exitCode == 0:
		text = "Update - {green}OK{endc}"
	else:
		text = "Update - {red}Error{endc}"
	ColorPrint(text)
	local.Exit()
#end define

def Upgrade(args):
	exitCode = RunAsRoot(["bash", "/usr/src/mytonctrl/scripts/upgrade.sh"])
	exitCode += RunAsRoot(["python3", "/usr/src/mytonctrl/scripts/upgrade.py"])

	if exitCode == 0:
		text = "Upgrade - {green}OK{endc}"
	else:
		text = "Upgrade - {red}Error{endc}"
	ColorPrint(text)
#end define

def CheckMytonctrlUpdate():
	gitPath = local.buffer.get("myDir")
	result = CheckUpdate(gitPath)
	if result:
		ColorPrint(local.Translate("update_available"))
#end define

def CheckUpdate(gitPath):
	args = ["git", "fetch", "--dry-run"]
	process = subprocess.run(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=gitPath, timeout=3)
	output = process.stdout.decode("utf-8")
	err = process.stderr.decode("utf-8")
	if len(output) > 0 or len(err) > 0:
		return True
	else:
		return False
#end define

def PrintTest(args):
	print(json.dumps(local.buffer, indent=4))
#end define

def Test(args):
	start = "kf8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIue"
	ok_arr = list()
	pending_arr = list()
	pending_arr.append(start)
	while True:
		try:
			TestWork(ok_arr, pending_arr)
		except KeyboardInterrupt:
			buff = ok_arr + pending_arr
			data = json.dumps(buff)
			file = open("testoutput.txt", "wt")
			file.write(data)
			file.close()
			break
		except:
			buff = ok_arr + pending_arr
			data = json.dumps(buff)
			file = open("testoutput.txt", "wt")
			file.write(data)
			file.close()
#end define

def Test2(args):
	Slashing(ton)
#end define

def Test3(args):
	Complaints(ton)
#end define

def TestWork(ok_arr, pending_arr):
	addr = pending_arr.pop(0)
	account = ton.GetAccount(addr)
	history = ton.GetAccountHistory(account, 1000)
	for item in history:
		outmsg = item.get("outmsg")
		if outmsg == 1:
			haddr = item.get("to")
		else:
			haddr = item.get("from")
		haddr = ton.HexAddr2Base64Addr(haddr)
		if haddr not in pending_arr and haddr not in ok_arr:
			pending_arr.append(haddr)
	ok_arr.append(addr)
	print(addr, len(ok_arr), len(pending_arr))
#end define

def PrintStatus(args):
	rootWorkchainEnabledTime_int = ton.GetRootWorkchainEnabledTime()
	config34 = ton.GetConfig34()
	config36 = ton.GetConfig36()
	totalValidators = config34["totalValidators"]
	onlineValidators = ton.GetOnlineValidators()
	if onlineValidators:
		onlineValidators = len(onlineValidators)
	oldStartWorkTime = config36.get("startWorkTime")
	if oldStartWorkTime is None:
		oldStartWorkTime = config34.get("startWorkTime")
	shardsNumber = ton.GetShardsNumber()
	validatorStatus = ton.GetValidatorStatus()
	config15 = ton.GetConfig15()
	config17 = ton.GetConfig17()
	fullConfigAddr = ton.GetFullConfigAddr()
	fullElectorAddr = ton.GetFullElectorAddr()
	startWorkTime = ton.GetActiveElectionId(fullElectorAddr)
	validatorIndex = ton.GetValidatorIndex()
	validatorEfficiency = ton.GetValidatorEfficiency()
	validatorWallet = ton.GetLocalWallet(ton.validatorWalletName)
	dbSize = ton.GetDbSize()
	offersNumber = ton.GetOffersNumber()
	complaintsNumber = ton.GetComplaintsNumber()
	if validatorWallet is not None:
		validatorAccount = ton.GetAccount(validatorWallet.addr)
	else:
		validatorAccount = None
	PrintTonStatus(startWorkTime, totalValidators, onlineValidators, shardsNumber, offersNumber, complaintsNumber)
	PrintLocalStatus(validatorIndex, validatorEfficiency, validatorWallet, validatorAccount, validatorStatus, dbSize)
	PrintTonConfig(fullConfigAddr, fullElectorAddr, config15, config17)
	PrintTimes(rootWorkchainEnabledTime_int, startWorkTime, oldStartWorkTime, config15)
#end define

def PrintTonStatus(startWorkTime, totalValidators, onlineValidators, shardsNumber, offersNumber, complaintsNumber):
	tpsAvg = ton.GetTpsAvg()
	tps1 = tpsAvg[0]
	tps5 = tpsAvg[1]
	tps15 = tpsAvg[2]
	allValidators = totalValidators
	newOffers = offersNumber.get("new")
	allOffers = offersNumber.get("all")
	newComplaints = complaintsNumber.get("new")
	allComplaints = complaintsNumber.get("all")
	tps1_text = bcolors.Green(tps1)
	tps5_text = bcolors.Green(tps5)
	tps15_text = bcolors.Green(tps15)
	tps_text = local.Translate("ton_status_tps").format(tps1_text, tps5_text, tps15_text)
	onlineValidators_text = GetColorInt(onlineValidators, border=allValidators*2/3, logic="more")
	allValidators_text = bcolors.Yellow(allValidators)
	validators_text = local.Translate("ton_status_validators").format(onlineValidators_text, allValidators_text)
	shards_text = local.Translate("ton_status_shards").format(bcolors.Green(shardsNumber))
	newOffers_text = bcolors.Green(newOffers)
	allOffers_text = bcolors.Yellow(allOffers)
	offers_text = local.Translate("ton_status_offers").format(newOffers_text, allOffers_text)
	newComplaints_text = bcolors.Green(newComplaints)
	allComplaints_text = bcolors.Yellow(allComplaints)
	complaints_text = local.Translate("ton_status_complaints").format(newComplaints_text, allComplaints_text)
	
	if startWorkTime == 0:
		election_text = bcolors.Yellow("closed")
	else:
		election_text = bcolors.Green("open")
	election_text = local.Translate("ton_status_election").format(election_text)

	ColorPrint(local.Translate("ton_status_head"))
	print(tps_text)
	print(validators_text)
	print(shards_text)
	print(offers_text)
	print(complaints_text)
	print(election_text)
	print()
#end define

def PrintLocalStatus(validatorIndex, validatorEfficiency, validatorWallet, validatorAccount, validatorStatus, dbSize):
	if validatorWallet is None:
		return
	adnlAddr = ton.adnlAddr
	walletAddr = validatorWallet.addr
	walletBalance = validatorAccount.balance
	cpuNumber = psutil.cpu_count()
	loadavg = GetLoadAvg()
	cpuLoad1 = loadavg[0]
	cpuLoad5 = loadavg[1]
	cpuLoad15 = loadavg[2]
	netLoadAvg = ton.GetNetLoadAvg()
	netLoad1 = netLoadAvg[0]
	netLoad5 = netLoadAvg[1]
	netLoad15 = netLoadAvg[2]
	validatorOutOfSync = validatorStatus.get("outOfSync")
	mytoncoreStatus_bool = GetServiceStatus("mytoncore")
	validatorStatus_bool = GetServiceStatus("validator")

	validatorIndex_text = GetColorInt(validatorIndex, 0, logic="more")
	validatorIndex_text = local.Translate("local_status_validator_index").format(validatorIndex_text)
	validatorEfficiency_text = GetColorInt(validatorEfficiency, 70, logic="more", ending=" %")
	validatorEfficiency_text = local.Translate("local_status_validator_efficiency").format(validatorEfficiency_text)
	adnlAddr_text = local.Translate("local_status_adnl_addr").format(bcolors.Yellow(adnlAddr))
	walletAddr_text = local.Translate("local_status_wallet_addr").format(bcolors.Yellow(walletAddr))
	walletBalance_text = local.Translate("local_status_wallet_balance").format(bcolors.Green(walletBalance, " GRM"))

	# CPU status
	cpuNumber_text = bcolors.Yellow(cpuNumber)
	cpuLoad1_text = GetColorInt(cpuLoad1, cpuNumber, logic="less")
	cpuLoad5_text = GetColorInt(cpuLoad5, cpuNumber, logic="less")
	cpuLoad15_text = GetColorInt(cpuLoad15, cpuNumber, logic="less")
	cpuLoad_text = local.Translate("local_status_cpu_load").format(cpuNumber_text, cpuLoad1_text, cpuLoad5_text, cpuLoad15_text)

	# Network status
	netLoad1_text = GetColorInt(netLoad1, 300, logic="less")
	netLoad5_text = GetColorInt(netLoad5, 300, logic="less")
	netLoad15_text = GetColorInt(netLoad15, 300, logic="less")
	netLoad_text = local.Translate("local_status_net_load").format(netLoad1_text, netLoad5_text, netLoad15_text)

	# Thread status
	mytoncoreStatus_text = local.Translate("local_status_mytoncore_status").format(GetColorStatus(mytoncoreStatus_bool))
	validatorStatus_text = local.Translate("local_status_validator_status").format(GetColorStatus(validatorStatus_bool))
	validatorOutOfSync_text = local.Translate("local_status_validator_out_of_sync").format(GetColorInt(validatorOutOfSync, 20, logic="less", ending=" s"))
	dbSize_text = local.Translate("local_status_db_size").format(GetColorInt(dbSize, 1000, logic="less", ending=" Gb"))

	ColorPrint(local.Translate("local_status_head"))
	print(validatorIndex_text)
	print(validatorEfficiency_text)
	print(adnlAddr_text)
	print(walletAddr_text)
	print(walletBalance_text)
	print(cpuLoad_text)
	print(netLoad_text)
	print(mytoncoreStatus_text)
	print(validatorStatus_text)
	print(validatorOutOfSync_text)
	print(dbSize_text)
	print()
#end define

def GetColorInt(data, border, logic, ending=None):
	if data is None:
		result = bcolors.Green("n/a")
	elif logic == "more":
		if data >= border:
			result = bcolors.Green(data, ending)
		else:
			result = bcolors.Red(data, ending)
	elif logic == "less":
		if data <= border:
			result = bcolors.Green(data, ending)
		else:
			result = bcolors.Red(data, ending)
	return result
#end define

def GetColorStatus(input):
	if input == True:
		result = bcolors.Green("working")
	else:
		result = bcolors.Red("not working")
	return result
#end define

def PrintTonConfig(fullConfigAddr, fullElectorAddr, config15, config17):
	validatorsElectedFor = config15["validatorsElectedFor"]
	electionsStartBefore = config15["electionsStartBefore"]
	electionsEndBefore = config15["electionsEndBefore"]
	stakeHeldFor = config15["stakeHeldFor"]
	minStake = config17["minStake"]
	maxStake = config17["maxStake"]

	fullConfigAddr_text = local.Translate("ton_config_configurator_addr").format(bcolors.Yellow(fullConfigAddr))
	fullElectorAddr_text = local.Translate("ton_config_elector_addr").format(bcolors.Yellow(fullElectorAddr))
	validatorsElectedFor_text = bcolors.Yellow(validatorsElectedFor)
	electionsStartBefore_text = bcolors.Yellow(electionsStartBefore)
	electionsEndBefore_text = bcolors.Yellow(electionsEndBefore)
	stakeHeldFor_text = bcolors.Yellow(stakeHeldFor)
	elections_text = local.Translate("ton_config_elections").format(validatorsElectedFor_text, electionsStartBefore_text, electionsEndBefore_text, stakeHeldFor_text)
	minStake_text = bcolors.Yellow(minStake)
	maxStake_text = bcolors.Yellow(maxStake)
	stake_text = local.Translate("ton_config_stake").format(minStake_text, maxStake_text)

	ColorPrint(local.Translate("ton_config_head"))
	print(fullConfigAddr_text)
	print(fullElectorAddr_text)
	print(elections_text)
	print(stake_text)
	print()
#end define

def PrintTimes(rootWorkchainEnabledTime_int, startWorkTime, oldStartWorkTime, config15):
	validatorsElectedFor = config15["validatorsElectedFor"]
	electionsStartBefore = config15["electionsStartBefore"]
	electionsEndBefore = config15["electionsEndBefore"]

	if startWorkTime == 0:
		startWorkTime = oldStartWorkTime
	#end if

	# Calculate time
	startValidation = startWorkTime
	endValidation = startWorkTime + validatorsElectedFor
	startElection = startWorkTime - electionsStartBefore
	endElection = startWorkTime - electionsEndBefore
	startNextElection = startElection + validatorsElectedFor

	# timestamp to datetime
	rootWorkchainEnabledTime = Timestamp2Datetime(rootWorkchainEnabledTime_int)
	startValidationTime = Timestamp2Datetime(startValidation)
	endValidationTime = Timestamp2Datetime(endValidation)
	startElectionTime = Timestamp2Datetime(startElection)
	endElectionTime = Timestamp2Datetime(endElection)
	startNextElectionTime = Timestamp2Datetime(startNextElection)
	
	# datetime to color text
	rootWorkchainEnabledTime_text = local.Translate("times_root_workchain_enabled_time").format(bcolors.Yellow(rootWorkchainEnabledTime))
	startValidationTime_text = local.Translate("times_start_validation_time").format(GetColorTime(startValidationTime, startValidation))
	endValidationTime_text = local.Translate("times_end_validation_time").format(GetColorTime(endValidationTime, endValidation))
	startElectionTime_text = local.Translate("times_start_election_time").format(GetColorTime(startElectionTime, startElection))
	endElectionTime_text = local.Translate("times_end_election_time").format(GetColorTime(endElectionTime, endElection))
	startNextElectionTime_text = local.Translate("times_start_next_election_time").format(GetColorTime(startNextElectionTime, startNextElection))

	ColorPrint(local.Translate("times_head"))
	print(rootWorkchainEnabledTime_text)
	print(startValidationTime_text)
	print(endValidationTime_text)
	print(startElectionTime_text)
	print(endElectionTime_text)
	print(startNextElectionTime_text)
#end define

def GetColorTime(datetime, timestamp):
	newTimestamp = GetTimestamp()
	if timestamp > newTimestamp:
		result = bcolors.Green(datetime)
	else:
		result = bcolors.Yellow(datetime)
	return result
#end define

def Seqno(args):
	try:
		walletName = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} seqno <wallet-name>")
		return
	wallet = ton.GetLocalWallet(walletName)
	seqno = ton.GetSeqno(wallet)
	print(walletName, "seqno:", seqno)
#end define

def CreatNewWallet(args):
	try:
		if len(args) == 0:
			walletName = ton.GenerateWalletName()
			workchain = 0
		else:
			workchain = args[0]
			walletName = args[1]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} nw <workchain-id> <wallet-name>")
		return
	wallet = ton.CreateWallet(walletName, workchain)
	table = list()
	table += [["Name", "Workchain", "Address"]]
	table += [[wallet.name, wallet.workchain, wallet.addr_init]]
	PrintTable(table)
#end define

def ActivateWallet(args):
	try:
		walletName = args[0]
	except Exception as err:
		walletName = "all"
	if walletName == "all":
		ton.WalletsCheck()
	else:
		wallet = ton.GetLocalWallet(walletName)
		if not os.path.isfile(wallet.bocFilePath):
			local.AddLog("Wallet {walletName} already activated".format(walletName=walletName), "warning")
			return
		account = ton.GetAccount(wallet.addr)
		if account.balance > 0:
			ton.SendFile(wallet.bocFilePath, wallet)
	ColorPrint("ActivateWallet - {green}OK{endc}")
#end define

def PrintWalletsList(args):
	table = list()
	table += [["Name", "Status", "Balance", "Workchain", "Address"]]
	data = ton.GetWallets()
	if (data is None or len(data) == 0):
		print("No data")
		return
	for wallet in data:
		account = ton.GetAccount(wallet.addr)
		if account.status != "active":
			wallet.addr = wallet.addr_init
		table += [[wallet.name, account.status, account.balance, wallet.workchain, wallet.addr]]
	PrintTable(table)
#end define

def ImportWalletFromFile(args):
	try:
		filePath = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} iw <wallet-path>")
		return
	if (".addr" in filePath):
		filePath = filePath.replace(".addr", '')
	if (".pk" in filePath):
		filePath = filePath.replace(".pk", '')
	if os.path.isfile(filePath + ".addr") == False:
		local.AddLog("ImportWalletFromFile error: Address file not found: " + filePath, "error")
		return
	if os.path.isfile(filePath + ".pk") == False:
		local.AddLog("ImportWalletFromFile error: Private key not found: " + filePath, "error")
		return
	if '/' in filePath:
		walletName = filePath[filePath.rfind('/')+1:]
	else:
		walletName = filePath
	copyfile(filePath + ".addr", ton.walletsDir + walletName + ".addr")
	copyfile(filePath + ".pk", ton.walletsDir + walletName + ".pk")
	ColorPrint("ImportWalletFromFile - {green}OK{endc}")
#end define

def SaveWalletAddressToFile(args):
	try:
		walletName = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} sw <wallet-name>")
		return
	wallet = ton.GetLocalWallet(walletName)
	wjson = {"name":wallet.name, "workchain":wallet.workchain, "addr":wallet.addr, "addr_hex":wallet.addr_hex, "addr_init":wallet.addr_init}
	text = json.dumps(wjson)
	file = open(walletName + "-addr.json", 'w')
	file.write(text)
	file.close()
	ColorPrint("SaveWalletAddressToFile - {green}OK{endc}")
#end define

def DeleteWallet(args):
	try:
		walletName = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} dw <wallet-name>")
		return
	wallet = ton.GetLocalWallet(walletName)
	wallet.Delete()
	ColorPrint("DeleteWallet - {green}OK{endc}")
#end define

def ViewAccountStatus(args):
	try:
		addr = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} vas <account-addr>")
		return
	addr = ton.GetDestinationAddr(addr)
	account = ton.GetAccount(addr)
	statusTable = list()
	statusTable += [["Address", "Status", "Balance"]]
	statusTable += [[addr, account.status, account.balance]]
	historyTable = GetHistoryTable(addr, 10)
	PrintTable(statusTable)
	print()
	PrintTable(historyTable)
#end define

def ViewAccountHistory(args):
	try:
		addr = args[0]
		limit = int(args[1])
	except:
		ColorPrint("{red}Bad args. Usage:{endc} vah <account-addr> <limit>")
		return
	table = GetHistoryTable(addr, limit)
	PrintTable(table)
#end define

def GetHistoryTable(addr, limit):
	addr = ton.GetDestinationAddr(addr)
	account = ton.GetAccount(addr)
	history = ton.GetAccountHistory(account, limit)
	table = list()
	typeText = ColorText("{red}{bold}{endc}")
	table += [["Time", typeText, "Grams", "From/To"]]
	for item in history:
		time = item.get("time")
		grams = item.get("value")
		outmsg = item.get("outmsg")
		if outmsg == 1:
			type = ColorText("{red}{bold}>>>{endc}")
			fromto = item.get("to")
		else:
			type = ColorText("{blue}{bold}<<<{endc}")
			fromto = item.get("from")
		fromto = ton.HexAddr2Base64Addr(fromto)
		#datetime = Timestamp2Datetime(time, "%Y.%m.%d %H:%M:%S")
		datetime = timeago(time)
		table += [[datetime, type, grams, fromto]]
	return table
#end define

def MoveGrams(args):
	try:
		walletName = args[0]
		destination = args[1]
		gram = args[2]
		if len(args) > 3:
			flags = args[3:]
		else:
			flags = list()
	except:
		ColorPrint("{red}Bad args. Usage:{endc} mg <wallet-name> <account-addr | bookmark-name> <gram-amount>")
		return
	wallet = ton.GetLocalWallet(walletName)
	destination = ton.GetDestinationAddr(destination)
	ton.MoveGrams(wallet, destination, gram, flags=flags)
	ColorPrint("MoveGrams - {green}OK{endc}")
#end define

def CreatNewBookmark(args):
	try:
		name = args[0]
		addr = args[1]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} nb <bookmark-name> <account-addr | domain-name>")
		return
	type = ton.GetStrType(addr)
	bookmark = dict()
	bookmark["name"] = name
	bookmark["type"] = type
	bookmark["addr"] = addr
	ton.AddBookmark(bookmark)
	ColorPrint("CreatNewBookmark - {green}OK{endc}")
#end define

def PrintBookmarksList(args):
	data = ton.GetBookmarks()
	if (data is None or len(data) == 0):
		print("No data")
		return
	table = list()
	table += [["Name", "Type", "Address / Domain", "Balance / Exp. date"]]
	for item in data:
		name = item.get("name")
		type = item.get("type")
		addr = item.get("addr")
		data = item.get("data")
		table += [[name, type, addr, data]]
	PrintTable(table)
#end define

def DeleteBookmark(args):
	try:
		name = args[0]
		type = args[1]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} db <bookmark-name> <bookmark-type>")
		return
	ton.DeleteBookmark(name, type)
	ColorPrint("DeleteBookmark - {green}OK{endc}")
#end define

# def CreatNewRule(args):
# 	print("fix me")
# #end define

# def PrintRulesList(args):
# 	data = ton.GetRules()
# 	if (data is None or len(data) == 0):
# 		print("No data")
# 		return
# 	table = list()
# 	table += [["Name", "fix me"]]
# 	for item in data:
# 		table += [[item.get("name"), item.get("fix me")]]
# 	PrintTable(table)
# #end define

# def DeleteRule(args):
# 	print("fix me")
# #end define

def PrintOffersList(args):
	offers = ton.GetOffers()
	print(json.dumps(offers, indent=4))
#end define

def VoteOffer(args):
	try:
		offerHash = args[0]
		offerHash = int(offerHash)
	except:
		ColorPrint("{red}Bad args. Usage:{endc} vo <offer-hash>")
		return
	ton.VoteOffer(offerHash)
	ColorPrint("VoteOffer - {green}OK{endc}")
#end define

def OfferDiff(args):
	try:
		offerHash = args[0]
		offerHash = int(offerHash)
	except:
		ColorPrint("{red}Bad args. Usage:{endc} od <offer-hash>")
		return
	ton.GetOfferDiff(offerHash)
#end define

def GetConfig(args):
	try:
		configId = args[0]
		configId = int(configId)
	except:
		ColorPrint("{red}Bad args. Usage:{endc} gc <config-id>")
		return
	data = ton.GetConfig(configId)
	text = json.dumps(data, indent=2)
	print(text)
#end define

def PrintComplaintsList(args):
	complaints = ton.GetComplaints()
	text = json.dumps(complaints, indent=4)
	print(text)
#end define

def VoteComplaint(args):
	try:
		electionId = args[0]
		complaintHash = args[1]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} vc <election-id> <complaint-hash>")
		return
	ton.VoteComplaint(electionId, complaintHash)
	ColorPrint("VoteComplaint - {green}OK{endc}")
#end define

def NewDomain(args):
	try:
		domainName = args[0]
		walletName = args[1]
		adnlAddr = args[2]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} nd <domain-name> <wallet-name> <site-adnl-addr>")
		return
	domain = dict()
	domain["name"] = domainName
	domain["adnlAddr"] = adnlAddr
	domain["walletName"] = walletName
	ton.NewDomain(domain)
	ColorPrint("NewDomain - {green}OK{endc}")
#end define

def PrintDomainsList(args):
	data = ton.GetDomains()
	if (data is None or len(data) == 0):
		print("No data")
		return
	table = list()
	table += [["Domain", "Wallet", "Expiration date", "ADNL address"]]
	for item in data:
		domainName = item.get("name")
		walletName = item.get("walletName")
		endTime = item.get("endTime")
		endTime = Timestamp2Datetime(endTime, "%d.%m.%Y")
		adnlAddr = item.get("adnlAddr")
		table += [[domainName, walletName, endTime, adnlAddr]]
	PrintTable(table)
#end define

def ViewDomainStatus(args):
	try:
		domainName = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} vds <domain-name>")
		return
	domain = ton.GetDomain(domainName)
	endTime = domain.get("endTime")
	endTime = Timestamp2Datetime(endTime, "%d.%m.%Y")
	adnlAddr = domain.get("adnlAddr")
	table = list()
	table += [["Domain", "Expiration date", "ADNL address"]]
	table += [[domainName, endTime, adnlAddr]]
	PrintTable(table)
#end define

def DeleteDomain(args):
	try:
		domainName = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} dd <domain-name>")
		return
	ton.DeleteDomain(domainName)
	ColorPrint("DeleteDomain - {green}OK{endc}")
#end define

def PrintElectionEntriesList(args):
	entries = ton.GetElectionEntries()
	print(json.dumps(entries, indent=4))
#end define

def VoteElectionEntry(args):
	if ton.validatorWalletName is None:
		ColorPrint("{red}You are not a validator, or this utility is not configured correctly.{endc}")
	ton.ReturnStake()
	ton.ElectionEntry()
	ColorPrint("VoteElectionEntry - {green}OK{endc}")
#end define

def PrintValidatorList(args):
	validators = ton.GetValidatorsList()
	print(json.dumps(validators, indent=4))
#end define

def GetSettings(args):
	try:
		name = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} get <settings-name>")
		return
	result = ton.GetSettings(name)
	print(json.dumps(result, indent=4))
#end define

def SetSettings(args):
	try:
		name = args[0]
		value = args[1]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} set <settings-name> <settings-value>")
		return
	result = ton.SetSettings(name, value)
	ColorPrint("SetSettings - {green}OK{endc}")
#end define



###
### Start of the program
###

if __name__ == "__main__":
	Init()
	console.Run()
#end if
