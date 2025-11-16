import os
import httpx  # 用于向 Mapbox 发出异步 HTTP 请求
import geopandas as gpd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware # 用于允许前端访问
from shapely.geometry import shape # 用于将 GeoJSON 转换为 Shapely 对象
from dotenv import load_dotenv # 用于加载 .env 文件

# -------------------------------------------------------------------
# 1. 加载配置和数据 (在服务器启动时执行一次)
# -------------------------------------------------------------------

# 加载 .env 文件中的环境变量
load_dotenv()
MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")

# 检查 Mapbox 令牌
if not MAPBOX_ACCESS_TOKEN:
    print("!!! 致命错误: MAPBOX_ACCESS_TOKEN 未在 .env 文件中设置。 !!!")
    exit(1)

# --- [新逻辑] 定义新文件名 ---
FILE_HOTSPOT_POLYGONS = "final_hotspot_polygons_weighted.geojson"
FILE_RESTAURANTS_DB = "restaurants_with_hotspot_scores.geojson"

gdf_hotspots = None
gdf_restaurants = None

# --- [新逻辑] 加载 *两个* GeoJSON 文件 ---
try:
    print(f"--- 正在加载热点区域文件: {FILE_HOTSPOT_POLYGONS} ---")
    gdf_hotspots = gpd.read_file(FILE_HOTSPOT_POLYGONS)
    gdf_hotspots = gdf_hotspots.to_crs("EPSG:4326")
    print(f"--- 成功加载 {len(gdf_hotspots)} 个最终热点多边形 ---")
    
    print(f"--- 正在加载餐厅数据库: {FILE_RESTAURANTS_DB} ---")
    gdf_restaurants = gpd.read_file(FILE_RESTAURANTS_DB)
    gdf_restaurants = gdf_restaurants.to_crs("EPSG:4326")
    print(f"--- 成功加载 {len(gdf_restaurants)} 家餐厅 ---")
    
    # 确保用于排序的列存在
    if 'weighted_score' not in gdf_restaurants.columns:
        print(f"!!! 警告: '{FILE_RESTAURANTS_DB}' 中未找到 'weighted_score' 列。")
        print("   > 将无法进行加权排序。请检查您的 Colab 脚本 C。")
        
    print("--- 后端服务器准备就绪 ---")

except FileNotFoundError as e:
    print(f"!!! 致命错误: 未找到数据文件 {e.filename}。 !!!")
    print("请确保 'final_hotspot_polygons_weighted.geojson' 和 'restaurants_with_hotspot_scores.geojson' 存在。")
    exit(1)
except Exception as e:
    print(f"!!! 致命错误: 加载 GeoJSON 时出错: {e} !!!")
    exit(1)


# -------------------------------------------------------------------
# 2. 初始化 FastAPI 应用
# -------------------------------------------------------------------
app = FastAPI(
    title="Where to DINE? API (v2 - 加权版)",
    description="一个用于推荐纽约市热点餐饮区的 API (返回餐厅列表)"
)

# 添加 CORS 中间件，允许所有来源 (用于开发)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建一个异步 HTTP 客户端 (用于 Mapbox API)
client = httpx.AsyncClient()

# -------------------------------------------------------------------
# 3. 创建 API 端点 (Endpoint)
# -------------------------------------------------------------------

@app.get("/")
def read_root():
    return {"status": "Where to DINE? API (v2) 正在运行。"}

@app.get("/api/hotspots")
async def get_all_hotspots():
    """
    [数据服务器]
    端点 1: 获取所有预先计算好的热点 *区域*。
    前端将用此数据在地图上绘制所有热点的灰色背景。
    """
    if gdf_hotspots is None:
        raise HTTPException(status_code=500, detail="服务器数据(Hotspots)未加载")
        
    # [修改] 返回新的加权多边形
    return gdf_hotspots.to_json()


@app.get("/api/recommend")
async def get_recommendations(
    lat: float = Query(..., description="用户点击的纬度"),
    lon: float = Query(..., description="用户点击的经度"),
    mode: str = Query(..., description="出行模式 ('driving' 或 'walking')"),
    minutes: int = Query(15, description="可达时间（分钟）")
):
    """
    [推荐引擎 - 已重构]
    端点 2: 返回在可达范围内、位于热点中、并按分数排序的 *餐厅列表*。
    """
    
    # --- 动作 A: 验证与代理 Mapbox API (同前) ---
    if mode == "driving":
        profile = "mapbox/driving"
    elif mode == "walking":
        profile = "mapbox/walking"
    else:
        raise HTTPException(status_code=400, detail="模式(mode)必须是 'driving' 或 'walking'")

    mapbox_url = (
        f"https://api.mapbox.com/isochrone/v1/{profile}/"
        f"{lon},{lat}" # Mapbox 需要 经度,纬度
        f"?contours_minutes={minutes}"
        f"&polygons=true"
        f"&access_token={MAPBOX_ACCESS_TOKEN}"
    )

    try:
        response = await client.get(mapbox_url)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=500, detail=f"可达性服务错误: {e.response.text}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail="可达性服务连接失败")

    # --- 动作 B: 解析等时圈 (同前) ---
    try:
        isochrone_json = response.json()
        isochrone_geom_json = isochrone_json["features"][0]["geometry"]
        isochrone_polygon = shape(isochrone_geom_json)
    except (IndexError, KeyError):
        raise HTTPException(status_code=500, detail="Mapbox API 未返回有效的等时圈")

    # --- 动作 C: 空间相交 [新逻辑] ---
    # 与 *餐厅数据库* (gdf_restaurants) 进行相交
    results_gdf = gdf_restaurants[gdf_restaurants.geometry.intersects(isochrone_polygon)]

    if results_gdf.empty:
        # 没有餐厅在可达范围内
        return results_gdf.to_json() # 返回一个空的 GeoJSON FeatureCollection

    # --- 动作 D: 过滤 [新逻辑] ---
    # 过滤掉那些不在热点区域内的餐厅 (即 'weighted_score' 为 NaN/null 的)
    # Colab 脚本 C 在空间连接时，未在热点内的餐厅 'weighted_score' 为 NaN
    results_hotspots_gdf = results_gdf.dropna(subset=['weighted_score'])

    if results_hotspots_gdf.empty:
        # 在可达范围内有餐厅，但没有一家位于热点内
        return results_hotspots_gdf.to_json() # 返回一个空的 GeoJSON FeatureCollection

    # --- 动作 E: 排名 [新逻辑] ---
    # 根据 'weighted_score' 降序排序
    results_sorted_gdf = results_hotspots_gdf.sort_values(by="weighted_score", ascending=False)

    # --- 动作 F: 响应 [新逻辑] ---
    # 将最终的、排序后的 *餐厅点列表* 转换为 GeoJSON 字符串
    return results_sorted_gdf.to_json()


# -------------------------------------------------------------------
# 4. (可选) 用于本地运行服务器
# -------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    print("--- 正在启动 Uvicorn 本地服务器 (http://127.0.0.1:8000) ---")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)