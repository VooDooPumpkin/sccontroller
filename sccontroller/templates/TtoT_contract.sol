pragma solidity ^0.6.0;

import "./contracts/access/Ownable.sol";
import "./contracts/token/ERC721/ERC721.sol";

contract TokToTokContract is Ownable {

	address payable private _refund;
	address private _creator;
	address private _buyer;
	ERC721 private _ERC_contract;
	uint256 private _creator_token;
	uint256 private _buyer_token;
	uint256 private _status;
	
	event StatusChanged(uint256 indexed last_status, uint256 indexed cur_status);
	
    constructor (address creator, address ERC_contract, address payable refund) public {
		_refund = refund;
		_creator = creator;
		_ERC_contract = ERC721(ERC_contract);
		_status = 1;
		emit StatusChanged(0, 1);
    }

	modifier is_creator_approved() {
        require(_ERC_contract.getApproved(_creator_token) == address(this), "Approved: creator did not approve token transfer");
        _;
    }

	modifier is_buyer_approved() {
		require(_buyer_token != _creator_token, "Approved: it's creators token, not yours");
        require(_ERC_contract.getApproved(_buyer_token) == address(this), "Approved: buyer did not approve token transfer");
        _;
    }

	modifier is_contract_participant() {
        require(this.owner() == _msgSender() || _creator == _msgSender() || _buyer == _msgSender(), "Access: caller is not a contract participant");
        _;
    }
	
	function creator_approve(uint256 tokenId) public {
		require(_creator == _msgSender(), "Caller is not the creator");
		require(_status == 1, "Creator token has been already approved or contract was finished");
		require(_ERC_contract.getApproved(tokenId) == address(this), "Token hasn't been approved to this contract yet");
		_creator_token = tokenId;
		uint256 last_status = _status;
		_status = 2;
		emit StatusChanged(last_status, _status);
	}
	
	function buyer_approve(uint256 tokenId) is_creator_approved public {
		require(_status == 2, "Buyer token has been already approved or contract was finished");
		require(tokenId != _creator_token, "Approved: it's creators token, not yours");
		require(_ERC_contract.getApproved(tokenId) == address(this), "Token hasn't been approved to this contract yet");
		_buyer = _msgSender();
		_buyer_token = tokenId;
		uint256 last_status = _status;
		_status = 3;
		emit StatusChanged(last_status, _status);
		force_deal();
	}
	
	
	function force_deal() is_creator_approved is_buyer_approved public {
		_ERC_contract.transferFrom(_creator, _buyer, _creator_token);
		_ERC_contract.transferFrom(_buyer, _creator, _buyer_token);
		uint256 last_status = _status;
		_status = 4;
		emit StatusChanged(last_status, _status);
	}
	

    function kill() virtual onlyOwner public {
        selfdestruct(_refund);
    }
}
