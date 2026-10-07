package com.hydromate.mobile

import com.hydromate.mobile.ui.*
import com.hydromate.mobile.ui.settings.ConnectionDraft
import org.junit.Assert.*
import org.junit.Test
import java.util.concurrent.CompletableFuture
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

class AeroBehaviorTest {
    @Test fun lateTowerAResponseCannotReplaceTowerBOrDemo() {
        val gate = RequestFence()
        val towerA = "http://localhost:8000\ntower-a"
        val towerB = "http://localhost:8000\ntower-b"
        val started = CountDownLatch(1)
        val release = CountDownLatch(1)
        val ticketA = gate.begin(towerA)
        val delayed = CompletableFuture.supplyAsync {
            started.countDown()
            check(release.await(3, TimeUnit.SECONDS))
            "old tower A response"
        }
        try {
            assertTrue(started.await(3, TimeUnit.SECONDS))
            gate.invalidate()
            val ticketB = gate.begin(towerB)
            release.countDown()
            assertEquals("old tower A response", delayed.get(3, TimeUnit.SECONDS))
            assertFalse(gate.accepts(ticketA, towerB))
            assertFalse(gate.accepts(ticketA, towerA))
            assertTrue(gate.accepts(ticketB, towerB))
            // Entering demo or leaving Activity must revoke the in-flight real result.
            gate.invalidate()
            assertFalse(gate.accepts(ticketB, towerB))
        } finally { release.countDown() }
    }

    @Test fun demoRequiresExplicitSelectionAndIsDeterministic() {
        assertNull(PreviewSupport.load(0))
        assertEquals(PreviewSupport.load(1), PreviewSupport.load(1))
        val data = PreviewSupport.load(1) as ReadingState.Ready
        assertEquals(20, data.values.size)
        assertTrue(data.values.all { it.device == "test-demo-aero" && it.synthetic })
        assertTrue(data.values.all { it.received < data.checked })
        assertEquals(1, (PreviewSupport.load(7) as ReadingState.Ready).values.size)
    }

    @Test fun demoCoversErrorsWithoutRelaxingMissingSensorContract() {
        assertEquals(ReadingState.Loading, PreviewSupport.load(2))
        assertTrue(PreviewSupport.load(3) is ReadingState.Empty)
        assertEquals(FailureKind.NETWORK, (PreviewSupport.load(4) as ReadingState.Failed).kind)
        assertEquals(FailureKind.INVALID, (PreviewSupport.load(6) as ReadingState.Failed).kind)
        val old = PreviewSupport.load(5) as ReadingState.Ready
        assertTrue(isOld(old.values.first().received, old.checked, PreviewSupport.referenceAge(5, 0)))
        assertNull(PreviewSupport.load(0)) // Error never selects fallback data.
    }

    @Test fun invalidDraftIsRetainedAndOnlyValidatedOnSave() {
        val draft = ConnectionDraft(" http://127.0.0.1:8000/ ", " tower-b ", " My tower ", "")
        assertThrows(IllegalArgumentException::class.java) { draft.validated() }
        assertEquals("", draft.age)
        val saved = draft.copy(age = "30").validated()
        assertEquals("tower-b", saved.device)
        assertEquals("http://127.0.0.1:8000", saved.server)
        assertEquals("My tower", saved.name)
        assertEquals(30, saved.ageMinutes)
    }
}
