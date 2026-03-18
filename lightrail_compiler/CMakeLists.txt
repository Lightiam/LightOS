cmake_minimum_required(VERSION 3.20)
project(LightRailCompiler VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------
option(LIGHTRAIL_BUILD_TESTS    "Build C++ unit tests"      ON)
option(LIGHTRAIL_BUILD_EXAMPLES "Build example programs"    ON)
option(LIGHTRAIL_ENABLE_TERNARY "Enable ternary compute"    ON)
option(LIGHTRAIL_ENABLE_ANALOG  "Enable analog compute"     ON)

# ---------------------------------------------------------------------------
# Header-only library target
# ---------------------------------------------------------------------------
add_library(lightrail_headers INTERFACE)
target_include_directories(lightrail_headers INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_compile_definitions(lightrail_headers INTERFACE
    $<$<BOOL:${LIGHTRAIL_ENABLE_TERNARY}>:LIGHTRAIL_TERNARY=1>
    $<$<BOOL:${LIGHTRAIL_ENABLE_ANALOG}>:LIGHTRAIL_ANALOG=1>
)

# ---------------------------------------------------------------------------
# Runtime stub library (intrinsic stubs for host emulation)
# ---------------------------------------------------------------------------
add_library(lightrail STATIC
    # Stub implementations (real ones are in the NCE kernel driver)
    # These allow host-side testing without hardware.
)
target_link_libraries(lightrail PUBLIC lightrail_headers)

# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------
if(LIGHTRAIL_BUILD_EXAMPLES)
    add_executable(cpp_tiled_pipeline
        examples/cpp_tiled_pipeline.cpp
    )
    target_link_libraries(cpp_tiled_pipeline PRIVATE lightrail)
endif()

# ---------------------------------------------------------------------------
# Install rules
# ---------------------------------------------------------------------------
install(TARGETS lightrail lightrail_headers
    EXPORT LightRailTargets
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)
install(DIRECTORY include/ DESTINATION include)
install(EXPORT LightRailTargets
    FILE LightRailTargets.cmake
    NAMESPACE LightRail::
    DESTINATION lib/cmake/LightRail
)

# ---------------------------------------------------------------------------
# Python extension (optional, requires pybind11)
# ---------------------------------------------------------------------------
find_package(pybind11 QUIET)
if(pybind11_FOUND)
    pybind11_add_module(lightrail_ext
        # src/bindings.cpp  # (future: Python/C++ bridge)
    )
    target_link_libraries(lightrail_ext PRIVATE lightrail)
endif()
