# Kubernetes Manifests for Test Automation

Bu klasör, test otomasyon sistemini Kubernetes üzerinde çalıştırmak için gerekli tüm YAML dosyalarını içerir.

## 📁 Dosyalar

```
manifests/
├── 01-namespace.yaml                  # Namespace oluşturur
├── 02-configmap.yaml                  # Configuration (node_count parametresi)
├── 03-chrome-node-deployment.yaml     # Chrome Node pod'larını deploy eder
├── 04-chrome-node-service.yaml        # Chrome Node'lara erişim için service
├── 05-test-controller-deployment.yaml # Test Controller pod'unu deploy eder
└── README.md                           # Bu dosya
```

## 🏗️ Mimari

### Gereksinimler (Interview Requirements)

✅ **Two Distinct Pods:**
1. **Test Case Controller Pod** (Deployment) - Test case'leri okur ve yönetir
2. **Chrome Node Pod** (Deployment) - Selenium testlerini headless Chrome'da çalıştırır

✅ **Inter-Pod Communication:**
- Kubernetes Service (ClusterIP) kullanarak
- DNS-based service discovery: `chrome-node-service.test-automation.svc.cluster.local`

✅ **Dynamic Chrome Node Creation:**
- `node_count` parameter ile kontrol edilir (min=1, max=5)
- ConfigMap'te tanımlanır
- kubectl scale ile dinamik olarak değiştirilebilir

```
┌─────────────────────────────────────────────────────┐
│         Kubernetes Namespace (test-automation)      │
│                                                      │
│  ┌────────────────────────────────┐                │
│  │   Test Controller Pod          │                │
│  │   (Deployment - replicas: 1)   │                │
│  │                                 │                │
│  │  - Reads test cases             │                │
│  │  - Manages test execution       │                │
│  │  - Distributes to Chrome Nodes  │                │
│  └──────────────┬──────────────────┘                │
│                 │                                    │
│                 │ HTTP/REST API                     │
│                 │ (Selenium Commands)               │
│                 │                                    │
│                 ▼                                    │
│  ┌─────────────────────────────┐                   │
│  │  chrome-node-service        │  ← Service (DNS)  │
│  │  (ClusterIP)                │                   │
│  └──────────┬──────────────────┘                   │
│             │                                        │
│             │ Load Balances                         │
│             │                                        │
│    ┌────────┼────────┬─────────────┬──────────┐    │
│    ▼        ▼        ▼             ▼          ▼    │
│  ┌────┐  ┌────┐  ┌────┐  ...   ┌────┐            │
│  │CN 1│  │CN 2│  │CN 3│         │CN n│            │
│  └────┘  └────┘  └────┘         └────┘            │
│  Chrome Node Deployment (replicas: 1-5)            │
│  Based on node_count parameter                     │
│                                                      │
│  ConfigMap: test-automation-config                  │
│  - node_count: 2 (default, min=1, max=5)          │
└─────────────────────────────────────────────────────┘
```

## 🚀 Hızlı Başlangıç

### Ön Gereksinimler

1. **Kubernetes cluster** (Minikube, Kind, veya cloud provider)
2. **kubectl** kurulu ve cluster'a bağlı
3. **Docker image'lar** build edilmiş:

```bash
# Image'ları build et
docker build -f docker/Dockerfile.chromenode -t chrome-node:latest .
docker build -f docker/Dockerfile.controller -t test-controller:latest .
```

### Deployment Adımları

#### Option 1: Tüm kaynakları tek komutla deploy et

```bash
kubectl apply -f k8s/manifests/
```

#### Option 2: Dosyaları sırayla deploy et

```bash
# 1. Namespace oluştur
kubectl apply -f k8s/manifests/01-namespace.yaml

# 2. ConfigMap oluştur (node_count parametresi burada)
kubectl apply -f k8s/manifests/02-configmap.yaml

# 3. Chrome Node deployment'ı deploy et
kubectl apply -f k8s/manifests/03-chrome-node-deployment.yaml

# 4. Chrome Node service'i oluştur (Inter-Pod Communication)
kubectl apply -f k8s/manifests/04-chrome-node-service.yaml

# 5. Chrome Node'ların hazır olmasını bekle
kubectl wait --for=condition=ready pod -l component=chrome-node -n test-automation --timeout=120s

# 6. Test Controller deployment'ı deploy et
kubectl apply -f k8s/manifests/05-test-controller-deployment.yaml
```

## 📊 Durum Kontrolü

### Tüm kaynakları görüntüle:
```bash
kubectl get all -n test-automation
```

### Pod'ları kontrol et:
```bash
kubectl get pods -n test-automation
```

Beklenen çıktı:
```
NAME                               READY   STATUS    RESTARTS   AGE
chrome-node-xxxxx-yyyyy            1/1     Running   0          2m
chrome-node-xxxxx-zzzzz            1/1     Running   0          2m
test-controller-xxxxx-wwwww        1/1     Running   0          1m
```

### Deployments kontrol et:
```bash
kubectl get deployments -n test-automation
```

### Service'leri kontrol et:
```bash
kubectl get svc -n test-automation
```

### ConfigMap'i görüntüle:
```bash
kubectl get configmap test-automation-config -n test-automation -o yaml
```

## 🔧 node_count Parametresi (Min=1, Max=5)

### Option 1: ConfigMap'i düzenle

```bash
# ConfigMap'i düzenle
kubectl edit configmap test-automation-config -n test-automation

# node_count değerini değiştir (1-5 arası)
# Ardından Chrome Node deployment'ı yeniden scale et
kubectl scale deployment chrome-node -n test-automation --replicas=3
```

### Option 2: kubectl scale kullan (Daha kolay)

```bash
# Chrome Node'ları 1'e scale et (minimum)
kubectl scale deployment chrome-node -n test-automation --replicas=1

# Chrome Node'ları 5'e scale et (maximum)
kubectl scale deployment chrome-node -n test-automation --replicas=5

# Chrome Node'ları 3'e scale et
kubectl scale deployment chrome-node -n test-automation --replicas=3

# Durumu kontrol et
kubectl get pods -n test-automation -l component=chrome-node
```

### Option 3: YAML dosyasını düzenle

[03-chrome-node-deployment.yaml](03-chrome-node-deployment.yaml) dosyasındaki `replicas: 2` değerini 1-5 arası değiştir:

```yaml
spec:
  replicas: 3  # 1-5 arası değer
```

Sonra apply et:
```bash
kubectl apply -f k8s/manifests/03-chrome-node-deployment.yaml
```

## 📝 Log'ları İzleme

### Test Controller log'larını görüntüle:
```bash
kubectl logs -n test-automation -l component=test-controller
```

### Test Controller log'larını canlı izle:
```bash
kubectl logs -n test-automation -l component=test-controller -f
```

### Chrome Node log'larını görüntüle:
```bash
kubectl logs -n test-automation -l component=chrome-node
```

### Belirli bir pod'un log'larını görüntüle:
```bash
kubectl logs -n test-automation <pod-name>
```

### Tüm Chrome Node log'larını aynı anda izle:
```bash
kubectl logs -n test-automation -l component=chrome-node --all-containers=true -f
```

## 🔄 Test'leri Yeniden Çalıştırma

Test Controller bir Deployment olduğundan sürekli çalışır. Test controller pod'u restart etmek için:

```bash
# Pod'u sil (Deployment otomatik yeni pod oluşturur)
kubectl delete pod -n test-automation -l component=test-controller

# VEYA deployment'ı restart et
kubectl rollout restart deployment test-controller -n test-automation

# Restart durumunu izle
kubectl rollout status deployment test-controller -n test-automation
```

## 🌐 Inter-Pod Communication Test

### Service DNS çözümlemesini test et:

```bash
# Temporary debug pod oluştur
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n test-automation -- sh

# Pod içinde:
curl http://chrome-node-service:4444/wd/hub/status

# VEYA tam DNS adı ile:
curl http://chrome-node-service.test-automation.svc.cluster.local:4444/wd/hub/status
```

### Test Controller'dan Chrome Node bağlantısını kontrol et:

```bash
# Test Controller pod'una exec ile bağlan
kubectl exec -it -n test-automation deployment/test-controller -- /bin/bash

# İçinde:
curl http://chrome-node-service:4444/wd/hub/status
```

## 🔍 Debug ve Troubleshooting

### Chrome Node'lar hazır değilse:

```bash
# Pod detaylarını görüntüle
kubectl describe pod -n test-automation -l component=chrome-node

# Log'ları kontrol et
kubectl logs -n test-automation -l component=chrome-node

# Events'leri görüntüle
kubectl get events -n test-automation --sort-by='.lastTimestamp'
```

### Test Controller bağlanamıyorsa:

```bash
# Deployment detaylarını görüntüle
kubectl describe deployment test-controller -n test-automation

# Pod'un log'larını görüntüle
kubectl logs -n test-automation -l component=test-controller

# Service endpoints kontrol et
kubectl get endpoints chrome-node-service -n test-automation
```

### Service bağlantısını test et:

```bash
# DNS resolution test
kubectl run -it --rm debug --image=busybox --restart=Never -n test-automation -- \
  nslookup chrome-node-service

# HTTP connection test
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n test-automation -- \
  curl -v http://chrome-node-service:4444/wd/hub/status
```

## 🌐 Selenium Grid UI'a Erişim

Chrome Node'ların Selenium Grid UI'ına erişmek için:

```bash
# Port forwarding yap
kubectl port-forward -n test-automation svc/chrome-node-service 4444:4444
```

Tarayıcıda aç: http://localhost:4444

## 🗑️ Temizleme

### Tüm kaynakları sil:

```bash
# Namespace'i sil (içindeki her şeyi siler)
kubectl delete namespace test-automation
```

### VEYA dosyaları tek tek sil:

```bash
kubectl delete -f k8s/manifests/
```

### Sadece Test Controller'ı sil:

```bash
kubectl delete deployment test-controller -n test-automation
```

## 📋 Resource Ayarları

### CPU ve Memory Limitleri:

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|-----------|----------------|--------------|
| Chrome Node | 500m | 1000m | 1Gi | 2Gi |
| Test Controller | 250m | 500m | 512Mi | 1Gi |

Bu değerleri değiştirmek için YAML dosyalarındaki `resources` bölümünü düzenleyin.

## 🎯 Interview Requirements Checklist

✅ **Two Distinct Pods:**
- [x] Test Case Controller Pod (Deployment)
- [x] Chrome Node Pod (Deployment)

✅ **Test Controller Responsibilities:**
- [x] Reads and manages test cases
- [x] Passes test cases to Chrome Nodes

✅ **Chrome Node Responsibilities:**
- [x] Runs Selenium tests in headless Chrome

✅ **Inter-Pod Communication:**
- [x] Kubernetes Service (chrome-node-service)
- [x] DNS-based service discovery
- [x] HTTP/REST API communication

✅ **Dynamic Chrome Node Creation:**
- [x] node_count parameter (min=1, max=5)
- [x] Configurable via ConfigMap
- [x] Scalable via kubectl scale

✅ **Kubernetes Resources:**
- [x] Deployment for Test Controller
- [x] Deployment for Chrome Nodes
- [x] Service for inter-pod communication
- [x] ConfigMap for configuration

## 📚 Mülakat İçin Önemli Kavramlar

### 1. **Deployment vs StatefulSet vs Job**
- **Deployment**: Stateless, scalable apps (kullandık - her iki pod için)
- **StatefulSet**: Stateful apps (database, etc.)
- **Job**: One-time tasks
- **DaemonSet**: One pod per node

### 2. **Inter-Pod Communication**
- **Service (ClusterIP)**: Internal load balancing
- **DNS**: `<service-name>.<namespace>.svc.cluster.local`
- **Environment Variables**: Service discovery
- **Direct Pod IP**: Not recommended (pods are ephemeral)

### 3. **Service Types**
- **ClusterIP**: Internal only (kullandık)
- **NodePort**: External access via Node IP
- **LoadBalancer**: Cloud provider LB
- **ExternalName**: DNS alias

### 4. **ConfigMap vs Secret**
- **ConfigMap**: Non-sensitive config (kullandık - node_count)
- **Secret**: Sensitive data (passwords, tokens)
- **Environment Variables**: Config injection
- **Volume Mounts**: File-based config

### 5. **Scaling**
- **Manual**: `kubectl scale`
- **HorizontalPodAutoscaler**: CPU/Memory based auto-scaling
- **VerticalPodAutoscaler**: Resource limit auto-adjustment

## 💡 Mülakatta Anlatacağın Mimari

1. **Test Controller Pod** (Deployment):
   - Test case'leri okur (features/ dizininden)
   - Selenium Grid endpoint'ini bulur (Service DNS ile)
   - Test'leri Chrome Node'lara gönderir (HTTP/WebDriver protocol)

2. **Chrome Node Pods** (Deployment):
   - Selenium Grid node olarak çalışır
   - Headless Chrome browser içerir
   - Test Controller'dan gelen komutları execute eder
   - Replicas: 1-5 (node_count parameter)

3. **Inter-Pod Communication**:
   - Service: `chrome-node-service` (ClusterIP)
   - DNS: `chrome-node-service.test-automation.svc.cluster.local`
   - Port: 4444 (Selenium Grid standard)
   - Protocol: HTTP/WebDriver

4. **Configuration**:
   - ConfigMap: `test-automation-config`
   - Parameters: node_count (1-5), max_retries, retry_delay
   - Environment Variables: Config injection to pods

## 🚀 Demo Komutları (Mülakatta Göster)

```bash
# 1. Deploy all resources
kubectl apply -f k8s/manifests/

# 2. Watch pods starting
kubectl get pods -n test-automation -w

# 3. Check deployment status
kubectl get deployments -n test-automation

# 4. Test inter-pod communication
kubectl exec -it -n test-automation deployment/test-controller -- \
  curl http://chrome-node-service:4444/wd/hub/status

# 5. Scale Chrome Nodes (demonstrate node_count)
kubectl scale deployment chrome-node -n test-automation --replicas=5
kubectl get pods -n test-automation -l component=chrome-node

# 6. View Test Controller logs
kubectl logs -f -n test-automation -l component=test-controller

# 7. Clean up
kubectl delete namespace test-automation
```

Bu yapı ile interview requirements'ları karşılayıp, Kubernetes bilgini gösterirsin! 🎯
