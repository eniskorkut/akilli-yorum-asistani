"""
Query Controller - Ana sorgu endpoint'leri

Bu modül, RAG sorgu işlemlerinin REST API endpoint'lerini sağlar.
FastAPI kullanarak HTTP isteklerini işler.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any
import time

from Interface.Models.QueryRequest import QueryRequest, BatchQueryRequest
from Interface.Models.QueryResponse import QueryResponse, BatchQueryResponse, ErrorResponse
# from Interface.Middleware.Authentication import require_api_key_header
# from Interface.Middleware.RateLimiting import require_rate_limiting
from DI import configure_container
from Logger import Logger


class QueryController:
    """
    Sorgu işlemleri için controller
    
    Bu sınıf, RAG sorgu işlemlerinin HTTP endpoint'lerini yönetir
    ve Application Layer ile Interface Layer arasında köprü görevi görür.
    """
    
    def __init__(self):
        """Controller'ı başlatır"""
        self.router = APIRouter(prefix="/api/v1/query", tags=["Query"])
        self._setup_routes()
        Logger.info("Query Controller başlatıldı")
    
    def _setup_routes(self):
        """Route'ları ayarlar"""
        
        @self.router.post("/", response_model=QueryResponse)
        async def query_product(
            request: QueryRequest
        ):
            """
            Tekil ürün sorgusu endpoint'i
            
            Bu endpoint, kullanıcının tek bir sorusunu işler ve
            AI destekli yanıt döndürür.
            
            Args:
                request: Sorgu isteği
                
            Returns:
                QueryResponse: Sorgu yanıtı
                
            Raises:
                HTTPException: Hata durumunda
            """
            try:
                start_time = time.time()
                
                Logger.info(f"Tekil sorgu isteği alındı: {request.question}")
                
                # DI Container'ı konfigüre et
                container = configure_container(use_mocks=request.use_mocks)
                app_service = container.get_query_application_service()
                
                # Sorgu parametrelerini hazırla
                kwargs = {}
                if request.product_url:
                    kwargs['product_url'] = request.product_url
                if request.max_reviews:
                    kwargs['max_reviews'] = request.max_reviews
                if request.use_mocks:
                    kwargs['use_mocks'] = True
                
                # Application Service ile sorgu yap
                result = app_service.query_product(request.question, **kwargs)
                
                processing_time = time.time() - start_time
                
                if result.get('success'):
                    # Başarılı yanıt
                    response = QueryResponse(
                        success=True,
                        answer=result.get('answer'),
                        question=result.get('question'),
                        total_reviews=result.get('total_reviews', 0),
                        used_reviews=result.get('used_reviews', 0),
                        processing_time=result.get('processing_time', processing_time),
                        timestamp=result.get('timestamp'),
                        metadata=result.get('metadata', {})
                    )
                    
                    Logger.info(f"Tekil sorgu başarıyla tamamlandı: {processing_time:.2f}s")
                    return response
                else:
                    # Hata yanıtı
                    error = result.get('error', {})
                    Logger.error(f"Tekil sorgu hatası: {error}")
                    
                    raise HTTPException(
                        status_code=400,
                        detail=ErrorResponse(
                            success=False,
                            error=error
                        ).dict()
                    )
                    
            except HTTPException:
                raise
            except Exception as e:
                Logger.error(f"Tekil sorgu beklenmeyen hata: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=ErrorResponse(
                        success=False,
                        error={
                            "error_code": "INTERNAL_ERROR",
                            "message": "Beklenmeyen bir hata oluştu",
                            "details": str(e),
                            "timestamp": time.time()
                        }
                    ).dict()
                )
        
        @self.router.post("/batch", response_model=BatchQueryResponse)
        async def batch_query_products(
            request: BatchQueryRequest
        ):
            """
            Toplu ürün sorgusu endpoint'i
            
            Bu endpoint, kullanıcının birden fazla sorusunu aynı anda
            işler ve toplu yanıt döndürür.
            
            Args:
                request: Toplu sorgu isteği
                
            Returns:
                BatchQueryResponse: Toplu sorgu yanıtı
                
            Raises:
                HTTPException: Hata durumunda
            """
            try:
                start_time = time.time()
                
                Logger.info(f"Toplu sorgu isteği alındı: {len(request.questions)} soru")
                
                # DI Container'ı konfigüre et
                container = configure_container(use_mocks=request.use_mocks)
                app_service = container.get_query_application_service()
                
                # Sorgu parametrelerini hazırla
                kwargs = {}
                if request.product_url:
                    kwargs['product_url'] = request.product_url
                if request.max_reviews:
                    kwargs['max_reviews'] = request.max_reviews
                if request.use_mocks:
                    kwargs['use_mocks'] = True
                
                # Her soru için işlem yap
                results = []
                successful_count = 0
                failed_count = 0
                
                for question in request.questions:
                    try:
                        result = app_service.query_product(question, **kwargs)
                        
                        if result.get('success'):
                            response = QueryResponse(
                                success=True,
                                answer=result.get('answer'),
                                question=result.get('question'),
                                total_reviews=result.get('total_reviews', 0),
                                used_reviews=result.get('used_reviews', 0),
                                processing_time=result.get('processing_time', 0),
                                timestamp=result.get('timestamp'),
                                metadata=result.get('metadata', {})
                            )
                            results.append(response)
                            successful_count += 1
                        else:
                            # Hata durumunda boş yanıt ekle
                            error_response = QueryResponse(
                                success=False,
                                answer=None,
                                question=question,
                                total_reviews=0,
                                used_reviews=0,
                                processing_time=0,
                                timestamp=time.time(),
                                metadata={"error": result.get('error', {})}
                            )
                            results.append(error_response)
                            failed_count += 1
                            
                    except Exception as e:
                        Logger.error(f"Soru işleme hatası: {question} - {e}")
                        
                        error_response = QueryResponse(
                            success=False,
                            answer=None,
                            question=question,
                            total_reviews=0,
                            used_reviews=0,
                            processing_time=0,
                            timestamp=time.time(),
                            metadata={"error": {"message": str(e)}}
                        )
                        results.append(error_response)
                        failed_count += 1
                
                total_processing_time = time.time() - start_time
                
                # Toplu yanıt oluştur
                batch_response = BatchQueryResponse(
                    success=successful_count > 0,
                    results=results,
                    total_questions=len(request.questions),
                    successful_questions=successful_count,
                    failed_questions=failed_count,
                    total_processing_time=total_processing_time,
                    timestamp=time.time()
                )
                
                Logger.info(f"Toplu sorgu tamamlandı: {successful_count}/{len(request.questions)} başarılı")
                return batch_response
                
            except HTTPException:
                raise
            except Exception as e:
                Logger.error(f"Toplu sorgu beklenmeyen hata: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=ErrorResponse(
                        success=False,
                        error={
                            "error_code": "INTERNAL_ERROR",
                            "message": "Beklenmeyen bir hata oluştu",
                            "details": str(e),
                            "timestamp": time.time()
                        }
                    ).dict()
                )
        
        @self.router.get("/suggestions")
        async def get_question_suggestions(
            partial_question: str = "",
            req: Request = None
        ):
            """
            Soru önerileri endpoint'i
            
            Bu endpoint, kullanıcıya soru önerileri sunar.
            
            Args:
                partial_question: Kısmi soru
                
            Returns:
                Dict: Soru önerileri
            """
            try:
                Logger.info(f"Soru önerisi isteği alındı: {partial_question}")
                
                # DI Container'ı konfigüre et
                container = configure_container(use_mocks=False)
                app_service = container.get_query_application_service()
                
                # Önerileri al
                suggestions = app_service.get_question_suggestions(partial_question)
                
                Logger.info(f"Soru önerileri döndürüldü: {len(suggestions.get('suggestions', []))} öneri")
                return suggestions
                
            except Exception as e:
                Logger.error(f"Soru önerisi hatası: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Soru önerileri alınamadı",
                        "message": str(e)
                    }
                )


# Global controller instance
query_controller = QueryController()


def get_query_controller() -> QueryController:
    """
    Query controller instance'ını döndürür
    
    Returns:
        QueryController: Controller instance'ı
    """
    return query_controller 