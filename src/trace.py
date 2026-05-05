from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Tracer


def init(name: str, endpoint: str) -> Tracer:
    provider = TracerProvider(resource=Resource(attributes={"service.name": name}))
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    return trace.get_tracer(name)
