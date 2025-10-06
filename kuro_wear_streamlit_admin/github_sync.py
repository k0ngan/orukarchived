# github_sync.py
import base64, json, os, pathlib, requests

class GitHubSync:
    def __init__(self, token: str, repo: str, branch: str = "main", base_path: str = ""):
        self.token = token
        self.repo = repo
        self.branch = branch
        self.base_path = base_path.strip("/")

        self.api_base = f"https://api.github.com/repos/{self.repo}/contents"

        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json",
        }

    def _full_path(self, path: str) -> str:
        if self.base_path:
            return f"{self.base_path.strip('/')}/{path.lstrip('/')}"
        return path.lstrip("/")

    def _get_sha(self, path: str) -> str | None:
        url = f"{self.api_base}/{self._full_path(path)}"
        resp = requests.get(url, params={"ref": self.branch}, headers=self.headers, timeout=30)
        if resp.status_code == 200:
            return resp.json().get("sha")
        return None  # no existe

    def put_bytes(self, path: str, data: bytes, message: str) -> dict:
        url = f"{self.api_base}/{self._full_path(path)}"
        content_b64 = base64.b64encode(data).decode("utf-8")
        sha = self._get_sha(path)
        payload = {
            "message": message,
            "content": content_b64,
            "branch": self.branch,
        }
        if sha:
            payload["sha"] = sha
        resp = requests.put(url, headers=self.headers, json=payload, timeout=60)
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"GitHub PUT {path} failed: {resp.status_code} {resp.text}")
        return resp.json()

    def put_text(self, path: str, text: str, message: str, encoding="utf-8") -> dict:
        return self.put_bytes(path, text.encode(encoding), message)

    # Helpers de tu app:
    def sync_products_json(self, local_products_json_path: str = "data/products.json", repo_path: str = "data/products.json"):
        data = pathlib.Path(local_products_json_path).read_text(encoding="utf-8")
        return self.put_text(repo_path, data, message="sync: update products.json")

    def sync_image_file(self, local_path: str, repo_path: str | None = None):
        lp = pathlib.Path(local_path)
        if repo_path is None:
            repo_path = f"data/images/{lp.name}"
        return self.put_bytes(repo_path, lp.read_bytes(), message=f"sync: image {lp.name}")

    def sync_folder_images(self, local_dir: str = "data/images", repo_dir: str = "data/images"):
        local = pathlib.Path(local_dir)
        if not local.exists():
            return []
        results = []
        for p in local.rglob("*"):
            if p.is_file():
                rel = p.relative_to(local).as_posix()
                results.append(self.sync_image_file(str(p), f"{repo_dir.rstrip('/')}/{rel}"))
        return results
