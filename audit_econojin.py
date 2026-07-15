#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
  🔍 EcoCoin & Econojin Platform Audit Script
  نسخه: 1.0.0
============================================================================

این اسکریپت وضعیت کامل پروژه econojin.com رو بررسی می‌کنه:

  ۱. ساختار پروژه
  ۲. قراردادهای هوشمند (آیا واقعاً وجود دارن؟)
  ۳. Wallet Integration
  ۴. Frontend Pages
  ۵. Backend API Routes
  ۶. Frontend ↔ Backend Connection
  ۷. User Profile/Account Integration
  ۸. Translation Files
  ۹. EcoCoin Integration Level
  ۱۰. UI/UX Quality Assessment

📍 محل اجرا:
  cd D:\\econojin.com
  python audit_econojin.py

نکته: این اسکریپت فقط خواندن انجام می‌ده، هیچ تغییری ایجاد نمی‌کنه.
============================================================================
"""

import os
import sys
import re
import json
import platform
from pathlib import Path
from datetime import datetime
from collections import defaultdict


# ============================================================
#  تنظیمات رنگ
# ============================================================
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"

    @staticmethod
    def enable_windows():
        if platform.system() == "Windows":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass


# ============================================================
#  کلاس ممیزی
# ============================================================
class EconojinAuditor:
    def __init__(self, project_path: str):
        self.path = Path(project_path).resolve()
        self.report = {
            "meta": {
                "project_path": str(self.path),
                "audit_date": datetime.now().isoformat(),
                "platform": platform.system(),
            },
            "sections": {},
            "score": 0,
            "grade": "",
            "critical_issues": [],
            "recommendations": [],
        }
        self.files_index = {}  # برای جستجوی سریع

    def _h(self, size: int) -> str:
        for u in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {u}"
            size /= 1024
        return f"{size:.1f} TB"

    def _read_file(self, path: Path, max_size: int = 1024 * 1024) -> str:
        """خواندن فایل با محدودیت حجم."""
        try:
            if path.stat().st_size > max_size:
                return ""
            for enc in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                try:
                    return path.read_text(encoding=enc, errors='ignore')
                except:
                    continue
        except:
            return ""
        return ""

    def _find_files(self, pattern: str, exclude_dirs: set = None) -> list[Path]:
        """پیدا کردن فایل‌ها با الگو."""
        if exclude_dirs is None:
            exclude_dirs = {'node_modules', '.git', '.next', '.nuxt', 'dist', 'build',
                           '__pycache__', '.venv', 'venv', '.pnpm-store', 'analysis_reports',
                           '.cleanup_backup', '.migration_backup'}

        results = []
        try:
            for root, dirs, files in os.walk(self.path):
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                for f in files:
                    if Path(f).match(pattern) or f.endswith(pattern.replace('*', '')):
                        results.append(Path(root) / f)
        except:
            pass
        return results

    def _grep_in_files(self, pattern: str, file_extensions: list[str] = None) -> list[tuple[Path, int, str]]:
        """جستجوی متن در فایل‌ها."""
        if file_extensions is None:
            file_extensions = ['.ts', '.tsx', '.js', '.jsx', '.py', '.json', '.sol']

        results = []
        for root, dirs, files in os.walk(self.path):
            dirs[:] = [d for d in dirs if d not in {'node_modules', '.git', '.next', '__pycache__',
                                                       '.venv', '.pnpm-store', 'analysis_reports'}]
            for f in files:
                fp = Path(root) / f
                if fp.suffix.lower() not in file_extensions:
                    continue
                content = self._read_file(fp)
                for i, line in enumerate(content.split('\n'), 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        results.append((fp, i, line.strip()[:100]))
        return results

    # ============================================================
    #  ۱. ساختار پروژه
    # ============================================================
    def audit_project_structure(self):
        print(f"\n{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}  ۱. ساختار پروژه{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")

        structure = {
            "apps": {"exists": False, "subdirs": []},
            "packages": {"exists": False, "subdirs": []},
            "infrastructure": {"exists": False},
            "smart_contracts": {"exists": False, "files": []},
            "frontend": {"exists": False, "framework": ""},
            "backend": {"exists": False, "framework": ""},
        }

        # بررسی apps/
        apps_dir = self.path / 'apps'
        if apps_dir.exists():
            structure["apps"]["exists"] = True
            structure["apps"]["subdirs"] = [d.name for d in apps_dir.iterdir() if d.is_dir()]
            print(f"  {C.GREEN}✓{C.RESET} apps/ وجود دارد")
            print(f"    {C.GRAY}زیرپوشه‌ها: {', '.join(structure['apps']['subdirs'])}{C.RESET}")
        else:
            print(f"  {C.RED}✗{C.RESET} apps/ وجود ندارد")

        # بررسی packages/
        packages_dir = self.path / 'packages'
        if packages_dir.exists():
            structure["packages"]["exists"] = True
            structure["packages"]["subdirs"] = [d.name for d in packages_dir.iterdir() if d.is_dir()]
            print(f"  {C.GREEN}✓{C.RESET} packages/ وجود دارد")

        # بررسی frontend (apps/web)
        web_dir = apps_dir / 'web'
        if web_dir.exists():
            structure["frontend"]["exists"] = True
            # تشخیص framework
            pkg_json = web_dir / 'package.json'
            if pkg_json.exists():
                content = self._read_file(pkg_json)
                if 'next' in content.lower():
                    structure["frontend"]["framework"] = "Next.js"
                elif 'vite' in content.lower():
                    structure["frontend"]["framework"] = "Vite"
                elif 'react' in content.lower():
                    structure["frontend"]["framework"] = "React"
            print(f"  {C.GREEN}✓{C.RESET} Frontend: {structure['frontend']['framework']}")

        # بررسی backend (apps/api یا apps/main.py)
        api_dir = apps_dir / 'api'
        if api_dir.exists():
            structure["backend"]["exists"] = True
            structure["backend"]["framework"] = "FastAPI"
            print(f"  {C.GREEN}✓{C.RESET} Backend: FastAPI")
        elif (apps_dir / 'main.py').exists():
            structure["backend"]["exists"] = True
            structure["backend"]["framework"] = "FastAPI"
            print(f"  {C.GREEN}✓{C.RESET} Backend: FastAPI (apps/main.py)")

        # بررسی قراردادهای هوشمند
        sol_files = self._find_files('*.sol')
        structure["smart_contracts"]["files"] = [str(f.relative_to(self.path)) for f in sol_files]
        structure["smart_contracts"]["exists"] = len(sol_files) > 0

        if sol_files:
            print(f"  {C.GREEN}✓{C.RESET} قراردادهای Solidity: {len(sol_files)} فایل")
            for f in sol_files[:5]:
                print(f"    {C.GRAY}• {f.relative_to(self.path)}{C.RESET}")
        else:
            print(f"  {C.RED}✗{C.RESET} قرارداد Solidity پیدا نشد!")
            self.report["critical_issues"].append("هیچ فایل .sol در پروژه وجود ندارد")

        self.report["sections"]["structure"] = structure
        return structure

    # ============================================================
    #  ۲. قراردادهای هوشمند
    # ============================================================
    def audit_smart_contracts(self):
        print(f"\n{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}  ۲. قراردادهای هوشمند{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")

        contracts_audit = {
            "solidity_files": [],
            "ecocoin_contract": False,
            "ecocredit_contract": False,
            "ecoreputation_contract": False,
            "ecobond_contract": False,
            "verification_registry": False,
            "deployment_scripts": [],
            "hardhat_config": False,
            "foundry_config": False,
            "openzeppelin_imports": False,
        }

        sol_files = self._find_files('*.sol')
        for f in sol_files:
            content = self._read_file(f)
            contracts_audit["solidity_files"].append({
                "path": str(f.relative_to(self.path)),
                "lines": content.count('\n'),
                "contracts": re.findall(r'contract\s+(\w+)', content),
            })

            if 'EcoCoin' in content:
                contracts_audit["ecocoin_contract"] = True
            if 'EcoCredit' in content:
                contracts_audit["ecocredit_contract"] = True
            if 'EcoReputation' in content:
                contracts_audit["ecoreputation_contract"] = True
            if 'EcoBond' in content:
                contracts_audit["ecobond_contract"] = True
            if 'VerificationRegistry' in content:
                contracts_audit["verification_registry"] = True
            if '@openzeppelin' in content:
                contracts_audit["openzeppelin_imports"] = True

        # بررسی hardhat/foundry
        hardhat_config = self.path / 'hardhat.config.ts'
        if hardhat_config.exists():
            contracts_audit["hardhat_config"] = True
            print(f"  {C.GREEN}✓{C.RESET} Hardhat config وجود دارد")

        foundry_config = self.path / 'foundry.toml'
        if foundry_config.exists():
            contracts_audit["foundry_config"] = True
            print(f"  {C.GREEN}✓{C.RESET} Foundry config وجود دارد")

        # بررسی deployment scripts
        deploy_files = self._find_files('deploy*.ts') + self._find_files('deploy*.js')
        contracts_audit["deployment_scripts"] = [str(f.relative_to(self.path)) for f in deploy_files]

        # نمایش نتایج
        if contracts_audit["ecocoin_contract"]:
            print(f"  {C.GREEN}✓{C.RESET} قرارداد EcoCoin")
        else:
            print(f"  {C.RED}✗{C.RESET} قرارداد EcoCoin پیدا نشد")
            self.report["critical_issues"].append("قرارداد EcoCoin وجود ندارد")

        if contracts_audit["ecocredit_contract"]:
            print(f"  {C.GREEN}✓{C.RESET} قرارداد EcoCredit")
        else:
            print(f"  {C.YELLOW}⚠{C.RESET} قرارداد EcoCredit پیدا نشد")

        if contracts_audit["openzeppelin_imports"]:
            print(f"  {C.GREEN}✓{C.RESET} OpenZeppelin imports")
        else:
            print(f"  {C.RED}✗{C.RESET} OpenZeppelin import نشده")

        if not contracts_audit["hardhat_config"] and not contracts_audit["foundry_config"]:
            print(f"  {C.RED}✗{C.RESET} هیچ build tool برای Solidity (hardhat/foundry)")
            self.report["critical_issues"].append("ابزار build قراردادهای هوشمند نصب نیست")

        self.report["sections"]["smart_contracts"] = contracts_audit
        return contracts_audit

    # ============================================================
    #  ۳. Wallet Integration
    # ============================================================
    def audit_wallet_integration(self):
        print(f"\n{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}  ۳. Wallet Integration{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")

        wallet_audit = {
            "wagmi": False,
            "rainbow_kit": False,
            "connect_wallet_button": False,
            "ethers_js": False,
            "web3modal": False,
            "wallet_files": [],
        }

        # بررسی package.json برای wagmi/rainbowkit
        pkg_files = self._find_files('package.json')
        for pf in pkg_files:
            content = self._read_file(pf)
            if 'wagmi' in content:
                wallet_audit["wagmi"] = True
                print(f"  {C.GREEN}✓{C.RESET} wagmi در {pf.relative_to(self.path)}")
            if 'rainbowkit' in content or '@rainbow-me/rainbowkit' in content:
                wallet_audit["rainbow_kit"] = True
                print(f"  {C.GREEN}✓{C.RESET} RainbowKit")
            if 'ethers' in content:
                wallet_audit["ethers_js"] = True
                print(f"  {C.GREEN}✓{C.RESET} ethers.js")
            if 'web3modal' in content:
                wallet_audit["web3modal"] = True

        # جستجوی connect wallet در فرانت‌اند
        connect_results = self._grep_in_files(r'connect\s*wallet|useAccount|useConnect|walletConnect', ['.ts', '.tsx', '.js', '.jsx'])
        if connect_results:
            wallet_audit["connect_wallet_button"] = True
            wallet_audit["wallet_files"] = [str(f.relative_to(self.path)) for f, _, _ in connect_results[:5]]
            print(f"  {C.GREEN}✓{C.RESET} Connect Wallet پیدا شد در {len(connect_results)} فایل")
        else:
            print(f"  {C.RED}✗{C.RESET} هیچ Connect Wallet در فرانت‌اند پیدا نشد")
            self.report["critical_issues"].append("Wallet integration در فرانت‌اند وجود ندارد")

        if not wallet_audit["wagmi"] and not wallet_audit["ethers_js"]:
            print(f"  {C.RED}✗{C.RESET} wagmi یا ethers.js نصب نیست")
            self.report["critical_issues"].append("کتابخانه wallet (wagmi/ethers) نصب نیست")

        self.report["sections"]["wallet"] = wallet_audit
        return wallet_audit

    # ============================================================
    #  ۴. Frontend Pages
    # ============================================================
    def audit_frontend_pages(self):
        print(f"\n{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}  ۴. Frontend Pages{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")

        pages_audit = {
            "total_pages": 0,
            "ecocoin_pages": [],
            "dashboard_page": False,
            "profile_page": False,
            "wallet_page": False,
            "staking_page": False,
            "marketplace_page": False,
            "pages_list": [],
        }

        # پیدا کردن page.tsx/page.tsx files
        page_files = self._find_files('page.tsx') + self._find_files('page.ts')
        pages_audit["total_pages"] = len(page_files)

        print(f"  {C.CYAN}کل صفحات:{C.RESET} {len(page_files)}")

        for pf in page_files[:30]:  # محدود به ۳۰
            rel = str(pf.relative_to(self.path))
            pages_audit["pages_list"].append(rel)
            content = self._read_file(pf).lower()

            if 'ecocoin' in content or 'eco-coin' in content:
                pages_audit["ecocoin_pages"].append(rel)
            if 'dashboard' in rel.lower():
                pages_audit["dashboard_page"] = True
            if 'profile' in rel.lower():
                pages_audit["profile_page"] = True
            if 'wallet' in rel.lower():
                pages_audit["wallet_page"] = True
            if 'staking' in rel.lower():
                pages_audit["staking_page"] = True
            if 'marketplace' in rel.lower() or 'market' in rel.lower():
                pages_audit["marketplace_page"] = True

        # نمایش
        if pages_audit["ecocoin_pages"]:
            print(f"  {C.GREEN}✓{C.RESET} صفحات EcoCoin: {len(pages_audit['ecocoin_pages'])}")
            for p in pages_audit["ecocoin_pages"][:5]:
                print(f"    {C.GRAY}• {p}{C.RESET}")
        else:
            print(f"  {C.RED}✗{C.RESET} هیچ صفحه‌ی EcoCoin در فرانت‌اند پیدا نشد")
            self.report["critical_issues"].append("صفحات EcoCoin در فرانت‌اند وجود ندارد")

        print(f"\n  {C.CYAN}صفحات کلیدی:{C.RESET}")
        for page, label in [
            ("dashboard_page", "داشبورد"),
            ("profile_page", "پروفایل"),
            ("wallet_page", "کیف پول"),
            ("staking_page", "استیکینگ"),
            ("marketplace_page", "بازار"),
        ]:
            if pages_audit[page]:
                print(f"    {C.GREEN}✓{C.RESET} {label}")
            else:
                print(f"    {C.RED}✗{C.RESET} {label}")

        self.report["sections"]["frontend_pages"] = pages_audit
        return pages_audit

    # ============================================================
    #  ۵. Backend API Routes
    # ============================================================
    def audit_backend_routes(self):
        print(f"\n{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}  ۵. Backend API Routes{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")

        routes_audit = {
            "total_routes": 0,
            "ecocoin_routes": [],
            "wallet_routes": False,
            "staking_routes": False,
            "user_routes": False,
            "routes_list": [],
        }

        # پیدا کردن فایل‌های route
        route_files = self._find_files('*.py')
        route_patterns = []

        for rf in route_files:
            content = self._read_file(rf)
            # پیدا کردن @router یا @app decorator
            matches = re.findall(r'@(?:router|app)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']', content)
            if matches:
                routes_audit["total_routes"] += len(matches)
                for method, path in matches:
                    route_patterns.append({
                        "file": str(rf.relative_to(self.path)),
                        "method": method.upper(),
                        "path": path,
                    })

                    if 'ecocoin' in path.lower() or 'eco-coin' in path.lower():
                        routes_audit["ecocoin_routes"].append({
                            "file": str(rf.relative_to(self.path)),
                            "method": method.upper(),
                            "path": path,
                        })
                    if 'wallet' in path.lower():
                        routes_audit["wallet_routes"] = True
                    if 'stake' in path.lower():
                        routes_audit["staking_routes"] = True
                    if 'user' in path.lower() or 'auth' in path.lower():
                        routes_audit["user_routes"] = True

        routes_audit["routes_list"] = route_patterns[:50]  # محدود

        print(f"  {C.CYAN}کل API routes:{C.RESET} {routes_audit['total_routes']}")

        if routes_audit["ecocoin_routes"]:
            print(f"  {C.GREEN}✓{C.RESET} EcoCoin routes: {len(routes_audit['ecocoin_routes'])}")
            for r in routes_audit["ecocoin_routes"][:5]:
                print(f"    {C.GRAY}• {r['method']} {r['path']} ({r['file']}){C.RESET}")
        else:
            print(f"  {C.RED}✗{C.RESET} هیچ EcoCoin API route پیدا نشد")
            self.report["critical_issues"].append("API routes مربوط به EcoCoin وجود ندارد")

        print(f"\n  {C.CYAN}Routes کلیدی:{C.RESET}")
        for route, label in [
            ("wallet_routes", "کیف پول"),
            ("staking_routes", "استیکینگ"),
            ("user_routes", "کاربر/احراز هویت"),
        ]:
            status = f"{C.GREEN}✓{C.RESET}" if routes_audit[route] else f"{C.RED}✗{C.RESET}"
            print(f"    {status} {label}")

        self.report["sections"]["backend_routes"] = routes_audit
        return routes_audit

    # ============================================================
    #  ۶. Frontend ↔ Backend Connection
    # ============================================================
    def audit_frontend_backend_connection(self):
        print(f"\n{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}  ۶. Frontend ↔ Backend Connection{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")

        connection_audit = {
            "api_calls": 0,
            "fetch_calls": 0,
            "axios_calls": 0,
            "api_client_files": [],
            "websocket_connections": 0,
            "api_base_url_configured": False,
            "sample_calls": [],
        }

        # جستجوی fetch/axios در فرانت‌اند
        api_results = self._grep_in_files(r'fetch\s*\(|axios\.(get|post|put|delete)|api\.(get|post)', ['.ts', '.tsx', '.js', '.jsx'])

        connection_audit["api_calls"] = len(api_results)

        for f, line, content in api_results[:20]:
            if 'fetch' in content:
                connection_audit["fetch_calls"] += 1
            if 'axios' in content:
                connection_audit["axios_calls"] += 1
            connection_audit["sample_calls"].append({
                "file": str(f.relative_to(self.path)),
                "line": line,
                "code": content[:80],
            })

        # بررسی api client files
        api_client_files = self._find_files('api*.ts') + self._find_files('api*.tsx') + self._find_files('client.ts')
        connection_audit["api_client_files"] = [str(f.relative_to(self.path)) for f in api_client_files[:10]]

        # بررسی env config
        env_files = self._find_files('.env*')
        for ef in env_files:
            content = self._read_file(ef)
            if 'API_URL' in content or 'NEXT_PUBLIC_API' in content or 'VITE_API' in content:
                connection_audit["api_base_url_configured"] = True
                break

        # WebSocket
        ws_results = self._grep_in_files(r'WebSocket|socket\.io|useWebSocket', ['.ts', '.tsx'])
        connection_audit["websocket_connections"] = len(ws_results)

        # نمایش
        print(f"  {C.CYAN}کل API calls در فرانت‌اند:{C.RESET} {connection_audit['api_calls']}")
        print(f"    • fetch: {connection_audit['fetch_calls']}")
        print(f"    • axios: {connection_audit['axios_calls']}")

        if connection_audit["api_client_files"]:
            print(f"\n  {C.GREEN}✓{C.RESET} فایل‌های API client:")
            for f in connection_audit["api_client_files"][:5]:
                print(f"    {C.GRAY}• {f}{C.RESET}")
        else:
            print(f"  {C.YELLOW}⚠{C.RESET} فایل API client مشخص نیست")

        if connection_audit["api_base_url_configured"]:
            print(f"  {C.GREEN}✓{C.RESET} API base URL در env تنظیم شده")
        else:
            print(f"  {C.YELLOW}⚠{C.RESET} API base URL در env تنظیم نشده")

        if connection_audit["websocket_connections"] > 0:
            print(f"  {C.GREEN}✓{C.RESET} WebSocket: {connection_audit['websocket_connections']} مورد")

        if connection_audit["api_calls"] == 0:
            print(f"  {C.RED}✗{C.RESET} هیچ API call در فرانت‌اند پیدا نشد!")
            self.report["critical_issues"].append("ارتباط frontend به backend وجود ندارد")

        self.report["sections"]["frontend_backend_connection"] = connection_audit
        return connection_audit

    # ============================================================
    #  ۷. User Profile/Account
    # ============================================================
    def audit_user_profile(self):
        print(f"\n{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}  ۷. User Profile/Account{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")

        profile_audit = {
            "auth_system": False,
            "profile_page": False,
            "user_model": False,
            "ecocoin_in_profile": False,
            "wallet_in_profile": False,
            "auth_files": [],
        }

        # بررسی auth
        auth_results = self._grep_in_files(r'nextauth|jsonwebtoken|jwt\.encode|authenticate|login\s*\(', ['.ts', '.tsx', '.py'])
        if auth_results:
            profile_audit["auth_system"] = True
            profile_audit["auth_files"] = list(set(str(f.relative_to(self.path)) for f, _, _ in auth_results))[:5]
            print(f"  {C.GREEN}✓{C.RESET} سیستم احراز هویت: {len(auth_results)} مورد")

        # بررسی profile page
        profile_pages = self._find_files('profile*') + [p for p in self._find_files('page.tsx') if 'profile' in str(p).lower()]
        if profile_pages:
            profile_audit["profile_page"] = True
            print(f"  {C.GREEN}✓{C.RESET} صفحه‌ی پروفایل وجود دارد")
        else:
            print(f"  {C.RED}✗{C.RESET} صفحه‌ی پروفایل پیدا نشد")

        # بررسی user model در backend
        user_model_results = self._grep_in_files(r'class\s+User|model\s+User|users?\s*\(.*Base\)', ['.py'])
        if user_model_results:
            profile_audit["user_model"] = True
            print(f"  {C.GREEN}✓{C.RESET} User model در backend")

        # بررسی EcoCoin در پروفایل
        ecocoin_in_profile = self._grep_in_files(r'ecocoin|eco_coin|ecoBalance|ecoWallet', ['.ts', '.tsx'])
        if ecocoin_in_profile:
            profile_audit["ecocoin_in_profile"] = True
            print(f"  {C.GREEN}✓{C.RESET} EcoCoin در فرانت‌اند: {len(ecocoin_in_profile)} مورد")
        else:
            print(f"  {C.RED}✗{C.RESET} EcoCoin در فرانت‌اند اصلاً استفاده نشده")
            self.report["critical_issues"].append("EcoCoin در فرانت‌اند پروژه統合 نشده")

        self.report["sections"]["user_profile"] = profile_audit
        return profile_audit

    # ============================================================
    #  ۸. Translation Files
    # ============================================================
    def audit_translations(self):
        print(f"\n{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}  ۸. Translation Files{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")

        translation_audit = {
            "i18n_library": "",
            "translation_files": [],
            "languages": [],
            "ecocoin_translations": False,
            "total_keys": 0,
        }

        # بررسی i18n libraries
        pkg_files = self._find_files('package.json')
        for pf in pkg_files:
            content = self._read_file(pf)
            if 'next-intl' in content:
                translation_audit["i18n_library"] = "next-intl"
                print(f"  {C.GREEN}✓{C.RESET} next-intl")
            if 'i18next' in content or 'react-i18next' in content:
                translation_audit["i18n_library"] = "i18next"
                print(f"  {C.GREEN}✓{C.RESET} i18next")
            if '@formatjs' in content or 'react-intl' in content:
                translation_audit["i18n_library"] = "react-intl"

        # پیدا کردن فایل‌های translation
        trans_files = (
            self._find_files('*.json', {'node_modules', '.git', '.next', '__pycache__', '.venv'}) +
            self._find_files('messages*') +
            self._find_files('locales*') +
            self._find_files('i18n*')
        )

        # فیلتر کردن فایل‌های ترجمه
        for tf in trans_files:
            if any(x in str(tf).lower() for x in ['node_modules', '.next', 'package', 'tsconfig', 'lock']):
                continue
            content = self._read_file(tf)
            if not content.strip().startswith('{'):
                continue
            try:
                data = json.loads(content)
                if isinstance(data, dict) and len(data) > 5:
                    translation_audit["translation_files"].append(str(tf.relative_to(self.path)))
                    # تشخیص زبان
                    if 'fa' in str(tf).lower() or 'ir' in str(tf).lower():
                        translation_audit["languages"].append('fa')
                    if 'en' in str(tf).lower():
                        translation_audit["languages"].append('en')
                    # بررسی ecocoin
                    if 'ecocoin' in content.lower() or 'eco_coin' in content.lower():
                        translation_audit["ecocoin_translations"] = True
                    translation_audit["total_keys"] += len(data)
            except:
                continue

        # حذف تکرارها
        translation_audit["languages"] = list(set(translation_audit["languages"]))
        translation_audit["translation_files"] = list(set(translation_audit["translation_files"]))[:10]

        print(f"  {C.CYAN}کتابخانه:{C.RESET} {translation_audit['i18n_library'] or 'نامشخص'}")
        print(f"  {C.CYAN}فایل‌های ترجمه:{C.RESET} {len(translation_audit['translation_files'])}")
        print(f"  {C.CYAN}زبان‌ها:{C.RESET} {', '.join(translation_audit['languages']) or 'نامشخص'}")

        if translation_audit["ecocoin_translations"]:
            print(f"  {C.GREEN}✓{C.RESET} ترجمه‌های EcoCoin وجود دارد")
        else:
            print(f"  {C.RED}✗{C.RESET} هیچ ترجمه‌ای برای EcoCoin وجود ندارد")
            self.report["critical_issues"].append("ترجمه‌های EcoCoin وجود ندارد")

        self.report["sections"]["translations"] = translation_audit
        return translation_audit

    # ============================================================
    #  ۹. UI/UX Quality Assessment
    # ============================================================
    def audit_ui_ux_quality(self):
        print(f"\n{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}  ۹. UI/UX Quality Assessment{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")

        ui_audit = {
            "tailwind": False,
            "shadcn": False,
            "framer_motion": False,
            "total_components": 0,
            "custom_components": 0,
            "responsive_design": False,
            "dark_mode": False,
            "animations": 0,
            "icons_library": "",
            "loading_states": 0,
            "error_states": 0,
            "empty_states": 0,
            "pages_with_minimal_styling": [],
        }

        # بررسی package.json
        pkg_files = self._find_files('package.json')
        for pf in pkg_files:
            if 'web' not in str(pf) and 'frontend' not in str(pf):
                continue
            content = self._read_file(pf)
            if 'tailwindcss' in content:
                ui_audit["tailwind"] = True
            if '@radix-ui' in content or 'shadcn' in content:
                ui_audit["shadcn"] = True
            if 'framer-motion' in content:
                ui_audit["framer_motion"] = True
            if 'lucide-react' in content:
                ui_audit["icons_library"] = "lucide-react"
            elif '@heroicons' in content:
                ui_audit["icons_library"] = "heroicons"
            elif 'react-icons' in content:
                ui_audit["icons_library"] = "react-icons"

        # شمارش components
        component_files = self._find_files('*.tsx')
        ui_audit["total_components"] = len(component_files)

        # بررسی responsive
        responsive_results = self._grep_in_files(r'sm:|md:|lg:|xl:|responsive', ['.tsx', '.css'])
        ui_audit["responsive_design"] = len(responsive_results) > 10

        # بررسی dark mode
        dark_results = self._grep_in_files(r'dark:|darkMode|theme.*dark', ['.tsx', '.ts', '.css'])
        ui_audit["dark_mode"] = len(dark_results) > 5

        # بررسی animations
        anim_results = self._grep_in_files(r'animate|transition|motion\.|framer', ['.tsx', '.ts'])
        ui_audit["animations"] = len(anim_results)

        # بررسی loading/error/empty states
        loading_results = self._grep_in_files(r'loading|skeleton|spinner|isLoading', ['.tsx'])
        ui_audit["loading_states"] = len(loading_results)

        error_results = self._grep_in_files(r'error|ErrorBoundary|catch|onError', ['.tsx'])
        ui_audit["error_states"] = len(error_results)

        empty_results = self._grep_in_files(r'empty|noData|noResults|isEmpty', ['.tsx'])
        ui_audit["empty_states"] = len(empty_results)

        # بررسی صفحات با استایل حداقل (فایل‌های page.tsx کمتر از ۵۰ خط)
        page_files = self._find_files('page.tsx')
        for pf in page_files:
            content = self._read_file(pf)
            lines = content.count('\n')
            if lines < 50:
                ui_audit["pages_with_minimal_styling"].append({
                    "file": str(pf.relative_to(self.path)),
                    "lines": lines,
                })

        # نمایش
        print(f"  {C.CYAN}Tailwind CSS:{C.RESET} {'✓' if ui_audit['tailwind'] else '✗'}")
        print(f"  {C.CYAN}shadcn/ui:{C.RESET} {'✓' if ui_audit['shadcn'] else '✗'}")
        print(f"  {C.CYAN}Framer Motion:{C.RESET} {'✓' if ui_audit['framer_motion'] else '✗'}")
        print(f"  {C.CYAN}آیکون‌ها:{C.RESET} {ui_audit['icons_library'] or 'نامشخص'}")
        print(f"  {C.CYAN}کل کامپوننت‌ها:{C.RESET} {ui_audit['total_components']}")
        print(f"  {C.CYAN}Responsive:{C.RESET} {'✓' if ui_audit['responsive_design'] else '✗'}")
        print(f"  {C.CYAN}Dark Mode:{C.RESET} {'✓' if ui_audit['dark_mode'] else '✗'}")
        print(f"  {C.CYAN}انیمیشن‌ها:{C.RESET} {ui_audit['animations']}")
        print(f"  {C.CYAN}Loading states:{C.RESET} {ui_audit['loading_states']}")
        print(f"  {C.CYAN}Error states:{C.RESET} {ui_audit['error_states']}")
        print(f"  {C.CYAN}Empty states:{C.RESET} {ui_audit['empty_states']}")

        if ui_audit["pages_with_minimal_styling"]:
            print(f"\n  {C.YELLOW}⚠ صفحات با استایل حداقل (<۵۰ خط):{C.RESET}")
            for p in ui_audit["pages_with_minimal_styling"][:5]:
                print(f"    {C.GRAY}• {p['file']} ({p['lines']} خط){C.RESET}")

        if not ui_audit["framer_motion"]:
            self.report["recommendations"].append("Framer Motion نصب کنید برای انیمیشن‌ها")
        if not ui_audit["shadcn"]:
            self.report["recommendations"].append("shadcn/ui نصب کنید برای کامپوننت‌های حرفه‌ای")
        if ui_audit["animations"] < 10:
            self.report["recommendations"].append("انیمیشن‌های بیشتری اضافه کنید (صفحات بی‌روح هستند)")

        self.report["sections"]["ui_ux"] = ui_audit
        return ui_audit

    # ============================================================
    #  ۱۰. EcoCoin Integration Level
    # ============================================================
    def audit_ecocoin_integration(self):
        print(f"\n{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}  ۱۰. EcoCoin Integration Level{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")

        integration_audit = {
            "ecocoin_mentions": 0,
            "in_frontend": 0,
            "in_backend": 0,
            "in_smart_contracts": 0,
            "in_translations": 0,
            "in_config": 0,
            "integration_level": "none",
            "files_with_ecocoin": [],
        }

        # جستجوی ecocoin در کل پروژه
        ecocoin_results = self._grep_in_files(r'ecocoin|eco_coin|EcoCoin', ['.ts', '.tsx', '.py', '.sol', '.json', '.md'])

        integration_audit["ecocoin_mentions"] = len(ecocoin_results)

        for f, line, _ in ecocoin_results:
            rel = str(f.relative_to(self.path))
            integration_audit["files_with_ecocoin"].append(rel)
            if 'apps/web' in rel or 'apps/frontend' in rel or 'packages/' in rel:
                integration_audit["in_frontend"] += 1
            if 'apps/api' in rel or 'apps/main' in rel:
                integration_audit["in_backend"] += 1
            if '.sol' in rel:
                integration_audit["in_smart_contracts"] += 1
            if 'translation' in rel.lower() or 'locale' in rel.lower() or 'message' in rel.lower():
                integration_audit["in_translations"] += 1
            if 'package.json' in rel or 'tsconfig' in rel or '.env' in rel:
                integration_audit["in_config"] += 1

        # تشخیص سطح integration
        total = integration_audit["ecocoin_mentions"]
        if total == 0:
            integration_audit["integration_level"] = "none"
        elif total < 10:
            integration_audit["integration_level"] = "minimal"
        elif total < 50:
            integration_audit["integration_level"] = "partial"
        elif total < 200:
            integration_audit["integration_level"] = "substantial"
        else:
            integration_audit["integration_level"] = "full"

        level_colors = {
            "none": C.RED,
            "minimal": C.RED,
            "partial": C.YELLOW,
            "substantial": C.GREEN,
            "full": C.GREEN + C.BOLD,
        }
        color = level_colors[integration_audit["integration_level"]]

        print(f"  {C.CYAN}کل اشاره‌ها به EcoCoin:{C.RESET} {total}")
        print(f"  {C.CYAN}در Frontend:{C.RESET} {integration_audit['in_frontend']}")
        print(f"  {C.CYAN}در Backend:{C.RESET} {integration_audit['in_backend']}")
        print(f"  {C.CYAN}در Smart Contracts:{C.RESET} {integration_audit['in_smart_contracts']}")
        print(f"  {C.CYAN}در Translations:{C.RESET} {integration_audit['in_translations']}")
        print(f"  {C.CYAN}در Config:{C.RESET} {integration_audit['in_config']}")
        print(f"\n  {C.CYAN}سطح integration:{C.RESET} {color}{integration_audit['integration_level'].upper()}{C.RESET}")

        if integration_audit["integration_level"] in ["none", "minimal"]:
            self.report["critical_issues"].append(
                f"EcoCoin در پروژه integration نشده (سطح: {integration_audit['integration_level']})"
            )

        self.report["sections"]["ecocoin_integration"] = integration_audit
        return integration_audit

    # ============================================================
    #  محاسبه‌ی امتیاز و grade
    # ============================================================
    def calculate_score(self):
        score = 0
        max_score = 100

        # ساختار (۱۵ امتیاز)
        struct = self.report["sections"].get("structure", {})
        if struct.get("apps", {}).get("exists"): score += 5
        if struct.get("frontend", {}).get("exists"): score += 5
        if struct.get("backend", {}).get("exists"): score += 5

        # قراردادها (۲۰ امتیاز)
        contracts = self.report["sections"].get("smart_contracts", {})
        if contracts.get("ecocoin_contract"): score += 8
        if contracts.get("ecocredit_contract"): score += 4
        if contracts.get("ecoreputation_contract"): score += 4
        if contracts.get("hardhat_config") or contracts.get("foundry_config"): score += 4

        # Wallet (۱۵ امتیاز)
        wallet = self.report["sections"].get("wallet", {})
        if wallet.get("wagmi") or wallet.get("ethers_js"): score += 8
        if wallet.get("connect_wallet_button"): score += 7

        # Frontend pages (۱۵ امتیاز)
        pages = self.report["sections"].get("frontend_pages", {})
        if pages.get("ecocoin_pages"): score += 8
        if pages.get("dashboard_page"): score += 2
        if pages.get("profile_page"): score += 2
        if pages.get("wallet_page"): score += 3

        # Backend routes (۱۰ امتیاز)
        routes = self.report["sections"].get("backend_routes", {})
        if routes.get("ecocoin_routes"): score += 5
        if routes.get("user_routes"): score += 3
        if routes.get("wallet_routes"): score += 2

        # Connection (۱۰ امتیاز)
        connection = self.report["sections"].get("frontend_backend_connection", {})
        if connection.get("api_calls", 0) > 10: score += 5
        elif connection.get("api_calls", 0) > 0: score += 3
        if connection.get("api_base_url_configured"): score += 3
        if connection.get("websocket_connections", 0) > 0: score += 2

        # Translations (۵ امتیاز)
        trans = self.report["sections"].get("translations", {})
        if trans.get("i18n_library"): score += 2
        if trans.get("ecocoin_translations"): score += 3

        # UI/UX (۱۰ امتیاز)
        ui = self.report["sections"].get("ui_ux", {})
        if ui.get("tailwind"): score += 2
        if ui.get("shadcn"): score += 2
        if ui.get("framer_motion"): score += 2
        if ui.get("responsive_design"): score += 2
        if ui.get("animations", 0) > 10: score += 2

        self.report["score"] = min(score, max_score)

        if score >= 90:
            self.report["grade"] = "A+"
        elif score >= 80:
            self.report["grade"] = "A"
        elif score >= 70:
            self.report["grade"] = "B"
        elif score >= 50:
            self.report["grade"] = "C"
        elif score >= 30:
            self.report["grade"] = "D"
        else:
            self.report["grade"] = "F"

    # ============================================================
    #  تولید گزارش نهایی
    # ============================================================
    def generate_summary(self):
        self.calculate_score()

        print(f"\n{C.MAGENTA}{C.BOLD}{'═'*60}{C.RESET}")
        print(f"{C.MAGENTA}{C.BOLD}  📊 گزارش نهایی ممیزی{C.RESET}")
        print(f"{C.MAGENTA}{C.BOLD}{'═'*60}{C.RESET}")

        score = self.report["score"]
        grade = self.report["grade"]

        if grade in ["A+", "A"]:
            color = C.GREEN
        elif grade in ["B"]:
            color = C.YELLOW
        elif grade in ["C", "D"]:
            color = C.RED
        else:
            color = C.RED + C.BOLD

        print(f"\n  {C.CYAN}امتیاز کلی:{C.RESET} {color}{C.BOLD}{score}/100 (نمره {grade}){C.RESET}")

        # مشکلات بحرانی
        if self.report["critical_issues"]:
            print(f"\n  {C.RED}{C.BOLD}🚨 مشکلات بحرانی ({len(self.report['critical_issues'])}):{C.RESET}")
            for issue in self.report["critical_issues"]:
                print(f"    {C.RED}✗{C.RESET} {issue}")

        # توصیه‌ها
        if self.report["recommendations"]:
            print(f"\n  {C.YELLOW}{C.BOLD}💡 توصیه‌ها:{C.RESET}")
            for rec in self.report["recommendations"]:
                print(f"    {C.YELLOW}⚠{C.RESET} {rec}")

        # خلاصه‌ی وضعیت
        print(f"\n  {C.CYAN}وضعیت بخش‌ها:{C.RESET}")
        sections_status = [
            ("ساختار پروژه", "structure"),
            ("قراردادهای هوشمند", "smart_contracts"),
            ("Wallet Integration", "wallet"),
            ("Frontend Pages", "frontend_pages"),
            ("Backend Routes", "backend_routes"),
            ("Frontend↔Backend", "frontend_backend_connection"),
            ("User Profile", "user_profile"),
            ("Translations", "translations"),
            ("UI/UX Quality", "ui_ux"),
            ("EcoCoin Integration", "ecocoin_integration"),
        ]

        for label, key in sections_status:
            section = self.report["sections"].get(key, {})
            if not section:
                print(f"    {C.GRAY}○ {label}: بررسی نشده{C.RESET}")
            elif key == "ecocoin_integration":
                level = section.get("integration_level", "none")
                icon = "✓" if level in ["substantial", "full"] else ("⚠" if level == "partial" else "✗")
                color = C.GREEN if level in ["substantial", "full"] else (C.YELLOW if level == "partial" else C.RED)
                print(f"    {color}{icon}{C.RESET} {label}: {level}")
            elif key == "smart_contracts":
                ok = section.get("ecocoin_contract", False)
                print(f"    {C.GREEN if ok else C.RED}{'✓' if ok else '✗'}{C.RESET} {label}")
            elif key == "wallet":
                ok = section.get("wagmi", False) or section.get("ethers_js", False)
                print(f"    {C.GREEN if ok else C.RED}{'✓' if ok else '✗'}{C.RESET} {label}")
            else:
                print(f"    {C.GRAY}○ {label}: بررسی شد{C.RESET}")

        # ذخیره‌ی گزارش JSON
        report_dir = self.path / 'analysis_reports'
        report_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"ecocoin_audit_{ts}.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, ensure_ascii=False, indent=2, default=str)

        print(f"\n  {C.GRAY}گزارش JSON:{C.RESET} {report_file}")
        print(f"\n  {C.CYAN}برای تکمیل EcoCoin:{C.RESET}")
        print(f"    ۱. قراردادهای .sol را در contracts/ قرار دهید")
        print(f"    ۲. wagmi + RainbowKit را در frontend نصب کنید")
        print(f"    ۳. صفحات /dashboard, /wallet, /staking بسازید")
        print(f"    ۴. API routes برای EcoCoin در backend اضافه کنید")
        print(f"    ۵. ترجمه‌های EcoCoin را اضافه کنید")
        print(f"    ۶. UI را با shadcn/ui + Framer Motion بهبود دهید")

    # ============================================================
    #  اجرای کامل
    # ============================================================
    def run(self):
        print(f"\n{C.MAGENTA}{C.BOLD}╔{'═'*58}╗{C.RESET}")
        print(f"{C.MAGENTA}{C.BOLD}║  🔍 Econojin & EcoCoin Audit v1.0{' '*24}║{C.RESET}")
        print(f"{C.MAGENTA}{C.BOLD}║  مسیر: {str(self.path):<51}║{C.RESET}")
        print(f"{C.MAGENTA}{C.BOLD}║  تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M'):<46}║{C.RESET}")
        print(f"{C.MAGENTA}{C.BOLD}╚{'═'*58}╝{C.RESET}")

        if not self.path.exists():
            print(f"{C.RED}❌ مسیر پروژه وجود ندارد!{C.RESET}")
            return False

        self.audit_project_structure()
        self.audit_smart_contracts()
        self.audit_wallet_integration()
        self.audit_frontend_pages()
        self.audit_backend_routes()
        self.audit_frontend_backend_connection()
        self.audit_user_profile()
        self.audit_translations()
        self.audit_ui_ux_quality()
        self.audit_ecocoin_integration()
        self.generate_summary()

        return True


# ============================================================
#  ورودی
# ============================================================
def main():
    C.enable_windows()

    default_path = r"D:\econojin.com"
    project_path = sys.argv[1] if len(sys.argv) > 1 else default_path

    auditor = EconojinAuditor(project_path)
    success = auditor.run()

    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
