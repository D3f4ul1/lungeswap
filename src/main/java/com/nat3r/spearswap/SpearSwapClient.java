package com.nat3r.spearswap;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.keybinding.v1.KeyBindingHelper;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.option.KeyBinding;
import net.minecraft.client.util.InputUtil;
import net.minecraft.item.ItemStack;
import net.minecraft.util.Identifier;

import org.lwjgl.glfw.GLFW;

import java.util.Locale;

/**
 * Client entrypoint.
 *
 * <p>Behaviour is the original SpearSwapper logic, unchanged: scan the hotbar by display name,
 * select the spear, force an attack, revert one tick later.
 *
 * <p>The one deliberate change is the keybind category. The original registered into
 * {@code KeyBinding.Category.MOVEMENT}, which is the vanilla "Movement" group -- that is why the
 * bind showed up mixed in with WASD. It now has its own category.
 */
public class SpearSwapClient implements ClientModInitializer {

    public static final String MOD_ID = "spearswap";

    /**
     * MAPPING: Yarn has no {@code KeyMapping} class and no {@code Category.register}; it is
     * {@code KeyBinding.Category.create(Identifier)}. Verified non-idempotent by disassembly: it
     * throws {@code IllegalArgumentException("Category '%s' is already registered.")} on a repeat
     * id, so it must be evaluated exactly once -- hence {@code static final}.
     *
     * <p>The label resolves via {@code Category.getLabel()} ->
     * {@code id.toTranslationKey("key.category")} = {@code key.category.<namespace>.<path>}, which
     * is why the lang key is {@code key.category.spearswap.main}.
     */
    public static final KeyBinding.Category CATEGORY =
            KeyBinding.Category.create(Identifier.of(MOD_ID, "main"));

    private static KeyBinding swapKeyBinding;

    @Override
    public void onInitializeClient() {
        // Default key G, same as the original. The category is ours, so it no longer sits in the
        // Movement group.
        swapKeyBinding = KeyBindingHelper.registerKeyBinding(new KeyBinding(
                "key.spearswap.swap",
                InputUtil.Type.KEYSYM,
                GLFW.GLFW_KEY_G,
                CATEGORY));

        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            if (client.player != null && swapKeyBinding != null) {
                // MAPPING: consumeClick() does not exist on 1.21.11; wasPressed() is the
                // consuming variant (its bytecode decrements timesPressed).
                while (swapKeyBinding.wasPressed()) {
                    triggerSwap(client);
                }
            }
            SwapManager.tick(client);
        });
    }

    private void triggerSwap(MinecraftClient mc) {
        int targetSlot = -1;

        for (int slot = 0; slot < 9; slot++) {
            ItemStack stack = mc.player.getInventory().getStack(slot);
            // Original behaviour: match on the localised display name. Crude, but it catches any
            // spear regardless of how the item is registered.
            String name = stack.getName().getString().toLowerCase(Locale.ROOT);
            if (name.contains("spear") || name.contains("trident")) {
                targetSlot = slot;
                break;
            }
        }

        // MAPPING: `inventory.selectedSlot` is `private int selectedSlot` on 1.21.11; use the
        // accessor. (The original widened the field; the accessor is public API and needs no
        // widener.)
        int currentSlot = mc.player.getInventory().getSelectedSlot();

        if (targetSlot != -1 && targetSlot != currentSlot) {
            SwapManager.startSwap(targetSlot, currentSlot);
        }
    }
}
