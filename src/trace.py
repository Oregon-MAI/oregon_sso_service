from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from src.constants import JAEGER_ENDPOINT, SERVICE_NAME

provider = TracerProvider(resource=Resource(attributes={"service.name": SERVICE_NAME}))
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=JAEGER_ENDPOINT, insecure=True))
)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(SERVICE_NAME)
