package com.hydromate.mobile

/** Activity-thread ownership: invalidate on tower/source change and onStop. */
class RequestFence {
    data class Ticket(val generation: Long, val identity: String)
    private var generation = 0L
    private var current: Ticket? = null
    fun begin(identity: String): Ticket = Ticket(++generation, identity).also { current = it }
    fun invalidate() { generation++; current = null }
    fun accepts(ticket: Ticket, identity: String) = current == ticket && ticket.identity == identity
}
