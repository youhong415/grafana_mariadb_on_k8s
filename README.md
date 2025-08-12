# Kubernetes Stack: MariaDB + Flask + Prometheus + Grafana

## 專案概述 (Project Overview)
這個專案旨在展示如何在 Kubernetes (K8s) 環境中部署一個完整的應用與監控堆疊，包含：
- **MariaDB**: 資料庫服務。
- **Flask Web App**: 一個簡單的 Python Web 應用，連線至 MariaDB。
- **Prometheus**: 監控系統，負責收集 MariaDB 的效能指標。
- **Grafana**: 資料視覺化工具，用於展示 Prometheus 收集的指標。

所有元件都透過手動撰寫 Kubernetes YAML 檔案進行部署，不使用 Helm，以深入理解 K8s 物件。

## 核心知識點 (Key Concepts)
- **Kubernetes (K8s)**: 容器編排平台。
- **Docker**: 容器化技術。
- **PersistentVolume (PV) & PersistentVolumeClaim (PVC)**: K8s 中用於提供持久化儲存的機制，本專案使用 `hostPath` 類型，適合 Docker Desktop 環境。
- **Secret**: 安全地儲存敏感資訊 (如資料庫密碼)。
- **ConfigMap**: 儲存非敏感配置資料 (如 Prometheus 設定檔)。
- **Deployment**: 管理 Pod 的部署和擴展。
- **Service**: 為 Pod 提供穩定的網路存取方式 (`ClusterIP` 用於叢集內部存取，`NodePort` 用於從外部存取)。
- **mysqld-exporter**: MariaDB 的 Prometheus Exporter，作為 MariaDB Pod 的 Sidecar 運行，暴露資料庫效能指標。
- **映像命名慣例**: 所有自建 Docker 映像和 K8s 資源都使用 `grafana-mariadb-on-k8s-` 作為前綴。

## 前置條件 (Prerequisites)
- 已安裝並運行 **Docker Desktop** (需啟用 Kubernetes)。
- 已安裝 **kubectl** CLI 工具。
- 已安裝 **docker** CLI 工具。
- 已登入 **Docker Hub** (用於推送 Flask 應用映像)。

## 快速啟動 (Quick Start)

### 1. 準備 Flask 應用映像
- 確保 `app.py` 和 `requirements.txt` 位於專案根目錄。
- 根據 `requirements.txt` 內容，更新 `Dockerfile`。
- **建置並推送 Docker 映像**:
  ```bash
  # 替換 YOUR_DOCKERHUB_USERNAME 為您的 Docker Hub 用戶名
  docker build -t YOUR_DOCKERHUB_USERNAME/grafana_mariadb_on_k8s-flask-app:v2 .
  docker push YOUR_DOCKERHUB_USERNAME/grafana_mariadb_on_k8s-flask-app:v2
  ```
  **注意**: `k8s/flask-deployment.yaml` 中已預設使用 `youhongji/grafana_mariadb_on_k8s-flask-app:v2`。

### 2. 建立持久化儲存目錄
在專案根目錄下建立以下目錄，用於 K8s `hostPath` 持久化儲存:
```bash
mkdir mariadb-data
mkdir prometheus-data
mkdir grafana-data
```

### 3. 部署所有 Kubernetes 資源
所有 K8s YAML 檔案都位於 `k8s/` 目錄下。
```bash
kubectl apply -f k8s/
```

### 4. 驗證部署
檢查所有 Pod 和 Service 的狀態:
```bash
kubectl get pods
kubectl get svc
kubectl get pv
kubectl get pvc
kubectl get secret
```
確保所有 Pod 均為 `Running` 狀態。

## 存取應用與服務 (Accessing Applications and Services)

### Flask Web App
1.  獲取 Flask Service 的 NodePort:
    ```bash
    kubectl get svc grafana-mariadb-on-k8s-flask-service
    ```
    記下 `PORT(S)` 欄位中 `80:` 後面的埠號 (例如 `3XXXX`)。
2.  在瀏覽器中訪問: `http://localhost:3XXXX`
3.  測試資料庫連線: `http://localhost:3XXXX/db_version`

### Prometheus UI
1.  透過 Port-Forward 臨時存取 Prometheus UI:
    ```bash
    kubectl port-forward service/grafana-mariadb-on-k8s-prometheus-service 9090:9090
    ```
2.  在瀏覽器中訪問: `http://localhost:9090`
3.  在 "Status" -> "Targets" 頁面確認 `mariadb` 目標狀態為 `UP`。

### Grafana UI
1.  獲取 Grafana Service 的 NodePort:
    ```bash
    kubectl get svc grafana-mariadb-on-k8s-grafana-service
    ```
    記下 `PORT(S)` 欄位中 `80:` 後面的埠號 (例如 `3XXXX`)。
2.  在瀏覽器中訪問: `http://localhost:3XXXX`
3.  **首次登入**: 使用 `admin`/`admin`。
4.  **添加 Prometheus 資料來源**:
    - 導航至 "Configuration" (齒輪圖示) -> "Data sources" -> "Add data source" -> "Prometheus"。
    - URL: `http://grafana-mariadb-on-k8s-prometheus-service:9090`
    - 點擊 "Save & test"。
5.  **匯入 MariaDB 儀表板**:
    - 導航至 "Create" (加號圖示) -> "Import"。
    - 在 "Import via grafana.com" 輸入 ID: `7362`。
    - 選擇剛才添加的 Prometheus 資料來源，點擊 "Import"。
6.  **產生負載**: 如果儀表板顯示 "No data"，請嘗試重複訪問 Flask App 的 `/db_version` 端點，或直接對 MariaDB 執行一些查詢，以產生資料庫活動。

## 快速清理 (Quick Cleanup)
刪除所有部署的 Kubernetes 資源:
```bash
# 刪除所有 K8s 資源
kubectl delete -f k8s/

# 刪除持久化儲存目錄 (注意: 這會刪除所有資料!)
rmdir /s /q mariadb-data
rmdir /s /q prometheus-data
rmdir /s /q grafana-data
```
**注意**: `rmdir /s /q` 是 Windows 命令，在 Linux/macOS 上請使用 `rm -rf`。

## 故障排除 (Troubleshooting)
- **Pod 狀態為 `Pending`**: 通常是 PV/PVC 綁定問題或資源不足。使用 `kubectl describe pod <pod-name>` 查看事件。
- **Pod 狀態為 `CrashLoopBackOff`**: 應用程式內部錯誤或配置問題。使用 `kubectl logs <pod-name>` 查看應用程式日誌。
- **`ImagePullBackOff`**: Kubernetes 無法拉取 Docker 映像。請檢查映像名稱、標籤是否正確，以及映像是否已成功推送到 Docker Hub。
- **Grafana 顯示 "No data"**:
    - 檢查 Grafana 的 Prometheus 資料來源是否配置正確且測試成功。
    - 檢查 Prometheus UI 中 "Status" -> "Targets" 頁面，確認 MariaDB 目標是否為 `UP`。
    - 確保 MariaDB 有足夠的活動來產生指標。
