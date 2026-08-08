// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
contract EcoCoin is ERC20, AccessControl, ReentrancyGuard {
    bytes32 public constant STEWARD=keccak256("STEWARD");bytes32 public constant ORACLE=keccak256("ORACLE");
    uint256 public constant GENESIS=50_000_000e18;uint256 public constant MAX=1_000_000_000e18;
    uint256 public minted;uint256 public burned;address public treasury;
    uint256 public burnRate=50;uint256 public unstakeFee=500;uint256 public tresPct=30;
    struct Stake{uint256 amt;uint40 start;uint40 unlock;uint8 tier;}
    struct Tier{uint40 dur;uint16 apy;uint8 mult;uint256 min;}
    mapping(uint256=>Tier)public tiers;mapping(address=>mapping(uint256=>Stake))public stakes;
    event Minted(address indexed to,uint256 a,uint256 pid,string r);event Burned(address indexed f,uint256 a);event Staked(address indexed u,uint256 a,uint256 t);event Unstaked(address indexed u,uint256 a,uint256 rw,uint256 f);
    constructor(address _t) ERC20("EcoCoin","ECO"){require(_t!=address(0));_grantRole(DEFAULT_ADMIN_ROLE,msg.sender);_grantRole(STEWARD,msg.sender);treasury=_t;_mint(_t,GENESIS);minted=GENESIS;
        tiers[0]=Tier(90 days,800,12,1000e18);tiers[1]=Tier(180 days,1500,15,5000e18);tiers[2]=Tier(365 days,2500,20,10000e18);tiers[3]=Tier(730 days,5000,30,50000e18);}
    function mint(address to,uint256 a,uint256 pid,string calldata r) external onlyRole(ORACLE){require(to!=address(0)&&a>0&&totalSupply()+a<=MAX);_mint(to,a);minted+=a;emit Minted(to,a,pid,r);}
    function burn(uint256 a) external {require(a>0);_burn(msg.sender,a);burned+=a;emit Burned(msg.sender,a);}
    function transferWithBurn(address to,uint256 a) external returns(bool){uint256 f=(a*burnRate)/10000;uint256 tT=(f*tresPct)/100;uint256 tB=f-tT;_transfer(msg.sender,to,a-f);if(tT>0)_transfer(msg.sender,treasury,tT);if(tB>0)_burn(msg.sender,tB);return true;}
    function stake(uint256 tid) external nonReentrant {Tier storage t=tiers[tid];require(t.min>0&&stakes[msg.sender][tid].amt==0&&balanceOf(msg.sender)>=t.min);_transfer(msg.sender,address(this),t.min);stakes[msg.sender][tid]=Stake(t.min,uint40(block.timestamp),uint40(block.timestamp+t.dur),uint8(tid));emit Staked(msg.sender,t.min,tid);}
    function unstake(uint256 tid) external nonReentrant {Stake storage s=stakes[msg.sender][tid];require(s.amt>0);uint256 p=s.amt;uint256 rw=_rw(p,tid,block.timestamp-s.start);delete stakes[msg.sender][tid];uint256 fe=block.timestamp<s.unlock?(p*unstakeFee)/10000:0;uint256 uu=p-fe+rw;uint256 tT=(fe*tresPct)/100;uint256 tB=fe-tT;
        if(rw>0){require(totalSupply()+rw<=MAX);_mint(address(this),rw);minted+=rw;}
        _transfer(address(this),msg.sender,uu);if(tT>0)_transfer(address(this),treasury,tT);if(tB>0){_burn(address(this),tB);burned+=tB;}emit Unstaked(msg.sender,p,rw,fe);}
    function _rw(uint256 a,uint256 tid,uint256 d) internal view returns(uint256){Tier storage t=tiers[tid];return(a*t.apy*d)/(365 days*10000);}
    function setOracle(address o) external onlyRole(STEWARD){require(o!=address(0));_grantRole(ORACLE,o);}
    function setTreasury(address t) external onlyRole(STEWARD){require(t!=address(0));treasury=t;}
    function setFees(uint256 b,uint256 u,uint256 tp) external onlyRole(STEWARD){require(b<=500&&u<=1000&&tp<=100);burnRate=b;unstakeFee=u;tresPct=tp;}
    function getStake(address u,uint256 tid) external view returns(Stake memory){return stakes[u][tid];}
    function circSupply() external view returns(uint256){uint256 l=balanceOf(address(this));return totalSupply()>l?totalSupply()-l:0;}
}