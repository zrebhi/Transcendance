from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
from eth_account import Account
from .models import Tournament

# Se connecter à un nœud Ethereum (nœud local ou RPC)
web3 = Web3(Web3.HTTPProvider('https://eth-sepolia-public.unifra.io'))

# Définir votre clé privée
private_key = 'e3c4dd727e69bcbe43c2920b3da65ce7ab03f03917c2ac2580228ef2573882cc'

# Convertir la clé privée en objet Account
account = Account.from_key(private_key)

# Ajouter le middleware pour signer les transactions avec votre clé privée
web3.middleware_onion.add(construct_sign_and_send_raw_middleware(private_key))

my_account = account.address

# Charger l'ABI du smart contract
contract_abi = [
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_tournamentId",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "_participant1",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_participant2",
				"type": "string"
			},
			{
				"internalType": "int256",
				"name": "_scoreParticipant1",
				"type": "int256"
			},
			{
				"internalType": "int256",
				"name": "_scoreParticipant2",
				"type": "int256"
			}
		],
		"name": "addMatch",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_tournamentId",
				"type": "uint256"
			}
		],
		"name": "closeTournament",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string[]",
				"name": "_participants",
				"type": "string[]"
			}
		],
		"name": "createTournament",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"inputs": [],
		"name": "ErrorListOfParticipantEmpty",
		"type": "error"
	},
	{
		"inputs": [],
		"name": "ErrorOnlyOwnerFunction",
		"type": "error"
	},
	{
		"inputs": [],
		"name": "ErrorTournamentAlreadyClosed",
		"type": "error"
	},
	{
		"inputs": [],
		"name": "ErrorTournamentIsClosed",
		"type": "error"
	},
	{
		"inputs": [],
		"name": "ErrorTournamentNotExist",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_tournamentId",
				"type": "uint256"
			}
		],
		"name": "getTournamentMatches",
		"outputs": [
			{
				"components": [
					{
						"internalType": "string",
						"name": "participant1",
						"type": "string"
					},
					{
						"internalType": "string",
						"name": "participant2",
						"type": "string"
					},
					{
						"internalType": "int256",
						"name": "scoreParticipant1",
						"type": "int256"
					},
					{
						"internalType": "int256",
						"name": "scoreParticipant2",
						"type": "int256"
					}
				],
				"internalType": "struct TournamentContract.Match[]",
				"name": "",
				"type": "tuple[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_tournamentId",
				"type": "uint256"
			}
		],
		"name": "getTournamentParticipants",
		"outputs": [
			{
				"internalType": "string[]",
				"name": "",
				"type": "string[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "nextTournamentId",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]

# Adresse du smart contract déployé
contract_address = '0x1ee56BDdE0256EA994B36CD48b090Fa2fb9444f7'

# Créer un objet de contrat
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Exemple : Créer un nouveau tournoi
def create_tournament(participants):
    try:
        # Appel de la fonction de contrat pour créer un tournoi avec les participants donnés
        tx_hash = contract.functions.createTournament(participants).transact({'from': my_account})

        # Attendre la confirmation de la transaction
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        # Vérifier le statut de la transaction
        if receipt.status == 1:
            print("Le tournoi a été créé avec succès !")
            # Récupérer l'ID du tournoi à partir de la transaction
            tournament_id = contract.functions.nextTournamentId().call() - 1
            return tournament_id
        else:
            print("La création du tournoi a échoué.")
            return None
    except Exception as e:
        print("Erreur lors de la création du tournoi :", e)
        return None



# Exemple : Ajouter un match à un tournoi existant
def add_match_to_tournament(tournament_id, participant1, participant2, winner):
    try:
        # Appel de la fonction de contrat pour ajouter un match au tournoi avec les détails donnés
        tx_hash = contract.functions.addMatch(tournament_id, participant1, participant2, score1, score2).transact({'from': my_account})

        # Attendre la confirmation de la transaction
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        # Vérifier le statut de la transaction
        if receipt.status == 1:
            print("Le match a été ajouté avec succès au tournoi !")
        else:
            print("L'ajout du match au tournoi a échoué.")
    except Exception as e:
        print("Erreur lors de l'ajout du match au tournoi :", e)

# Exemple : Clôturer un tournoi existant
def close_tournament(tournament_id):
    try:
        # Appel de la fonction de contrat pour fermer le tournoi spécifié
        tx_hash = contract.functions.closeTournament(tournament_id).transact({'from': my_account})
		# Attendre la confirmation de la transaction
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        # Vérifier le statut de la transaction
        if receipt.status == 1:
            print("Le tournoi a été clôturé avec succès !")
			print_etherscan_transaction_url(tx_hash)
		else:
            print("La clôture du tournoi a échoué.")
    except Exception as e:
        print("Erreur lors de la clôture du tournoi :", e)


# Utilisation des fonctions
        

# tournament_id = create_tournament(["Participant 1", "Participant 2", "Participant 3", "Participant 4"])
# print(tournament_id)
# add_match_to_tournament(tournament_id, 'Participant 1', 'Participant 2', 3, 1)
# add_match_to_tournament(tournament_id, 'Participant 2', 'Participant 4', 0, 3)
# add_match_to_tournament(tournament_id, 'Participant 1', 'Participant 4', 3, 2)
# close_tournament(tournament_id)
#
# print(contract.functions.getTournamentParticipants(tournament_id).call())
# print(contract.functions.getTournamentMatches(tournament_id).call())

def print_etherscan_transaction_url(tx_hash):
    etherscan_url = 'https://sepolia.etherscan.io/tx/'
    print("Transaction URL:", etherscan_url + tx_hash.hex())

def set_tournament_in_blockchain(tournament):
	tournament_id = create_tournament(partipants.stringarray) # Rajouter None dans l'array
	for match in tournament.matches:
		add_match_to_tournament(tournament_id, match.participant1, match.participant2, match.scoreParticipant1, match.scoreParticipant2)
	close_tournament(tournament_id)
	print(contract.functions.getTournamentMatches(tournament_id).call())
