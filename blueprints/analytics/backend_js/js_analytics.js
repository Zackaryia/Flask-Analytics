window.addEventListener('beforeunload', function (e) {
    log_event('pageUnload')
});

function log_event(event_string) {
    $.post("{{ url_for('analytics.analytics_post') }}", {event: event_string})
};

function log_event(n){$.post("{{ url_for('analytics.analytics_post') }}",{event:n})}window.addEventListener("beforeunload",function(n){log_event("pageUnload")});